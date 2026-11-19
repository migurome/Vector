// Cliente BLE para configurar Vector desde Windows/Linux/macOS sin Chrome.
// Reutiliza el protocolo RTS de digital-dream-labs/vector-web-setup (vendor/, MIT) y sustituye
// navigator.bluetooth del navegador por el paquete `webbluetooth` (SimpleBLE).
//
// Uso:  node index.js [filtroNombre]      p. ej.  node index.js G4C7
// Luego en el prompt: wifi-scan · wifi-connect {ssid} {password} · status · ota-start {url} · ota-progress · help
const readline = require("readline");
const { Bluetooth } = require("webbluetooth");
const sodium = require("libsodium-wrappers");

// Modo cambio de Wi-Fi:  node index.js --wifi "SSID" "contraseña"   (escanea, conecta, muestra IP y sale)
const wifiMode = process.argv[2] === "--wifi";
if (wifiMode && !process.argv[4]) { console.log('Uso: node index.js --wifi "SSID" "contraseña"'); process.exit(1); }
const queue = wifiMode
  ? [["wifi-scan"], ["wifi-connect", process.argv[3], process.argv[4]], ["wifi-ip"], ["status"]]
  : null;
const filter = wifiMode ? "" : process.argv[2] || "";
let chosen = false;
globalThis.window = globalThis; // vectorBluetooth.js usa window.setInterval
// Node 21+ define un navigator de solo lectura: hay que redefinirlo.
Object.defineProperty(globalThis, "navigator", { configurable: true, value: {
  bluetooth: new Bluetooth({
    deviceFound: (device) => {
      const ok = !chosen && (device.name || "").startsWith("Vector") && device.name.includes(filter);
      if (ok) { chosen = true; console.log("Encontrado:", device.name); }
      return ok;
    },
  }),
} });

const { VectorBluetooth } = require("./vendor/vectorBluetooth.js");
const { IntBuffer } = require("./vendor/clad.js");
const handlers = {
  2: require("./vendor/rtsV2Handler.js").RtsV2Handler,
  3: require("./vendor/rtsV3Handler.js").RtsV3Handler,
  4: require("./vendor/rtsV4Handler.js").RtsV4Handler,
  5: require("./vendor/rtsV5Handler.js").RtsV5Handler,
  6: require("./vendor/rtsV6Handler.js").RtsV6Handler,
};

// Sesiones solo en memoria: cada ejecución pide PIN de nuevo (suficiente para configurar).
const sessions = { getSession: () => null, getKeys: () => null, setSession() {}, setKeys() {}, deleteSession() {}, save() {} };

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
let rts = null;

function prompt() {
  if (queue) {
    const cmd = queue.shift();
    if (!cmd) { console.log("\nListo. Comprueba arriba 'IPv4' y 'wifi state: online'."); process.exit(0); }
    console.log("\nvector> " + (cmd[0] === "wifi-connect" ? `wifi-connect "${cmd[1]}" ********` : cmd.join(" ")));
    if (rts.handleCli(cmd)) prompt();
    return;
  }
  rl.question("\x1b[32;1mvector>\x1b[0m ", (line) => {
    const args = line.trim().split(/\s+/).filter(Boolean);
    if (!args.length) return prompt();
    // wifi-connect con SSID/contraseña con espacios: usar comillas "..."
    const quoted = line.match(/"[^"]*"|\S+/g).map((a) => a.replace(/^"|"$/g, ""));
    if (rts.handleCli(quoted)) prompt();
  });
}

function onHandshake(version) {
  const Handler = handlers[version];
  if (!Handler) return console.log("Versión RTS desconocida:", version);
  console.log(`Vector usa RTS v${version}`);
  if (rts) rts.cleanup();
  rts = new Handler(ble, sodium, sessions);
  rts.onReadyForPin(() => rl.question("PIN que muestra Vector en la cara: ", (pin) => rts.enterPin(pin.trim())));
  rts.onEncryptedConnection(() => {
    console.log("Conexión cifrada OK. Escribe 'help' para ver comandos.");
    prompt();
  });
  rts.onCliResponse((out) => { console.log(out); prompt(); });
  rts.onPrint((out) => console.log(out));
  rts.onCommandDone(() => {});
  rts.onNewProgressBar(() => {});
  rts.onUpdateProgressBar((v, total) => process.stdout.write(`\rProgreso: ${Math.floor((v / total) * 100)}%   `));
  rts.onLogsDownloaded(() => {});
  ble.send([1].concat(IntBuffer.Int32ToLE(version)));
}

let ble;
sodium.ready.then(() => {
  ble = new VectorBluetooth();
  ble.onReceive({
    receive: (data) => {
      if (process.env.DEBUG) console.log("<-", Buffer.from(data).toString("hex"));
      if (data[0] === 1 && data.length === 5) onHandshake(IntBuffer.BufferToUInt32(data.slice(1)));
    },
  });
  ble.onDisconnected?.(() => { console.log("\nDesconectado del robot."); process.exit(0); });
  console.log("Buscando Vector... (robot en modo emparejamiento: doble pulsación en la base)");
  ble.tryConnect(null); // el filtro por nombre se aplica en deviceFound (aquí exige nombre exacto)
  // shortcut: si el saludo llega antes de suscribirnos se pierde; no se reintenta solo, hay que relanzar.
  setTimeout(() => {
    if (!rts) { console.log("\nNo llega el saludo del robot. Cierra (Ctrl+C), espera 5 s y vuelve a lanzar."); process.exit(1); }
  }, 20000);
});

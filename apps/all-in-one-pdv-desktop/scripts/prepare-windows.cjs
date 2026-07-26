const fs = require('node:fs');
const path = require('node:path');

const storePath = path.resolve(__dirname, '../electron/store.cjs');
const source = fs.readFileSync(storePath, 'utf8');
const legacy = "const fd = fs.openSync(temp, 'r');";
const windowsSafe = "const fd = fs.openSync(temp, 'r+');";

if (source.includes(legacy)) {
  fs.writeFileSync(storePath, source.replace(legacy, windowsSafe), 'utf8');
  console.log('Ajuste de persistência Windows aplicado.');
} else if (source.includes(windowsSafe)) {
  console.log('Persistência Windows já preparada.');
} else {
  throw new Error('Trecho de persistência esperado não foi encontrado em electron/store.cjs.');
}

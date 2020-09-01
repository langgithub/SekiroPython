const frida = require('frida');
const fs = require('fs');
const path = require('path');
const util = require('util');

const readFile = util.promisify(fs.readFile);

let session, script;
async function run() {
  const source = await readFile(path.join(__dirname, '_agent.js'), 'utf8');
  session = await frida.attach('iTunes');
  script = await session.createScript(source);
  script.message.connect(onMessage);
  await script.load();
  console.log(await script.exports.add(2, 3));
  console.log(await script.exports.sub(5, 3));
}

run().catch(onError);

function onError(error) {
  console.error(error.stack);
}

function onMessage(message, data) {
  if (message.type === 'send') {
    console.log(message.payload);
  } else if (message.type === 'error') {
    console.error(message.stack);
  }
}
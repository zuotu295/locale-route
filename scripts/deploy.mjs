import { pathToFileURL } from 'node:url';
import { makeDeployment, signer } from './studionet.mjs';
export function deploy(account) {
  return makeDeployment(account, new URL('../contracts/locale_route.py', import.meta.url), [], 'locale-route');
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  console.log(JSON.stringify(await deploy(await signer(process.env.STUDIONET_PRIVATE_KEY)), null, 2));
}

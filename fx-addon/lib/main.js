var data = require("sdk/self").data;
var pageMod = require("sdk/page-mod");

pageMod.PageMod({
  include: ["http://*","https://*","file:/*"],
  contentScriptFile: data.url("inject.js"),
  contentScriptWhen: 'start'
});

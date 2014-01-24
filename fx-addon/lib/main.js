var data = require("sdk/self").data;
var pageMod = require("sdk/page-mod");

var script = data.load("oracle.js");

pageMod.PageMod({
  include: ["http://*","https://*","file:/*"],
  contentScriptFile: data.url("inject.js"),
  contentScriptWhen: 'start',
  onAttach: function(worker) {
    worker.port.emit("inject", script);
  }
});

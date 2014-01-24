self.port.on("inject", function(script) {
  var scr = document.createElement('script');
  scr.appendChild(document.createTextNode(script));
  document.documentElement.appendChild(scr);
}, true);

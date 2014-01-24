
function createSessionID() {
  return 'something unique-ish';
}


function initializeOracle(session_id, listener_base) {
  session = session_id;
  if(! session) {
    var session = createSessionID();
    // we're going to want sessions to be initialsed *before* webdriver can 
    // do anything to do the document. TODO: need to work out a way to
    // create session IDs and have webdriver query for those and correlate
    // to webdriver sessions
  }
  if(! listener_base) {
    listener_base = 'http://localhost:3333';
  }

  function doPing(url) {
    var img = document.createElement('img');
    img.src = url;
    var remove = function(){document.body.removeChild(img)};
    img.addEventListener('load', remove,true);
    img.addEventListener('error', remove, true);
    document.body.appendChild(img);

  }

  function accessorPing(session) {
    doPing(listener_base+'/accessed/'+session);
  }

  function invocationPing(session, arg) {
    doPing(listener_base+'/invoked/'+session+'/'+arg);
  }

  // TODO: we probably don't want the oracle identifier to be static.
  // Initially let's go for a short-ish string that's unlikely to collide
  Object.prototype.__defineGetter__('QxZ', function() {
    accessorPing(session);
    return function(arg) {
      invocationPing(session, arg);
    }
  });
}

initializeOracle();
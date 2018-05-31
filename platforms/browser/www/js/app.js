// Dom7
var $$ = Dom7;

// Framework7 App main instance
var app  = new Framework7({
  root: '#app', // App root element
  id: 'io.framework7.testapp', // App bundle ID
  name: 'Framework7', // App name
  theme: 'auto', // Automatic theme detection
  // App root data
  data: function () {
    return {
      user: {
        firstName: 'John',
        lastName: 'Doe',
      },
    };
  },
  // App root methods
  methods: {
    helloWorld: function () {
      app.dialog.alert('Hello World!');
    },
  },
  // App routes
  routes: routes,
  // Enable panel left visibility breakpoint
  panel: {
    leftBreakpoint: 960,
  },
});

// Init/Create left panel view
var mainView = app.views.create('.view-left', {
  url: '/'
});

// Init/Create main view
var mainView = app.views.create('.view-main', {
  url: '/'
});
var catalogView = app.views.create('#view-books', {
  url: '/mybooks/'
});
var settingsView = app.views.create('#view-settings', {
  url: '/about/'
});



  function searchCheck(that) {
        if (that.value == "isbn_") {
            document.getElementById("isbn-check").style.display = "block";
            document.getElementById("author-check").style.display = "none";
            document.getElementById("title-check").style.display = "none";
        } else if (that.value == "author_") {
            document.getElementById("author-check").style.display = "block";
            document.getElementById("isbn-check").style.display = "none";
            document.getElementById("title-check").style.display = "none";
        } else if (that.value == "title_") {
            document.getElementById("title-check").style.display = "block";
            document.getElementById("author-check").style.display = "none";
            document.getElementById("isbn-check").style.display = "none";
        } else {
            document.getElementById("ifYes").style.display = "none";
        }
    }

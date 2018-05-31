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


// addbook html functions
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

// function paymentMethod1() {
//   var checkRate = document.getElementById("for-rent");

//         if (checkRate.checked == true) {
//             document.getElementById("price-rate").style.display = "block";
//         } else {
//             document.getElementById("price-rate").style.display = "none";
//         }
// }

// function paymentMethod2() {
//   var checkSale = document.getElementById("for-sale");

//         if (checkSale.checked == true) {
//             document.getElementById("price-sale").style.display = "block";
//         } else {
//             document.getElementById("price-sale").style.display = "none";
//         }
// }

// // signup html functions

// function signUp1() {
//   document.getElementById("signUp1").style.display = "none";
//   document.getElementById("signUp2").style.display = "block";
// }

// function signUp2() {
//   document.getElementById("signUp1").style.display = "block";
//   document.getElementById("signUp2").style.display = "none"; 
// }

// function signUp3() {
//   document.getElementById("signUp1").style.display = "none";
//   document.getElementById("signUp2").style.display = "none";
//   document.getElementById("signUp3").style.display = "block";
// }

// function signUp4() {
//   document.getElementById("signUp1").style.display = "none";
//   document.getElementById("signUp2").style.display = "block";
//   document.getElementById("signUp3").style.display = "none";
// }

// function showTab() {
//   document.getElementById('showTab1').style.display = "block";
// }

// function test() {
// var toggle  = document.getElementById("toggle");
// var content = document.getElementById("content");

// toggle.addEventListener("click", function() {
//   content.classList.toggle("show");
// });
// }

routes = [
  {
    path: '/',
    url: './index.html',
  },
  {
    path: '/about/',
    url: './pages/about.html',
  },
  {
    path: '/form/',
    url: './pages/form.html',
  },
  {
    path: '/educational/',
    url: './pages/educational.html',
  },
  {
    path: '/fictional/',
    url: './pages/fictional.html',
  },
  {
    path: '/non-fictional/',
    url: './pages/non-fictional.html',
  },
  {
    path: '/login/',
    url: './pages/login.html',
  },
  {
    path: '/item/',
    url: './pages/item-page.html',
  },
  {
    path: '/logged/',
    url: './logged.html',
  },
  {
    path: '/userprof/',
    url: './pages/profile.html',
  },
  {
    path: '/item/',
    url: './pages/item-page.html',
  },
  {
    path: '/dashboard-comment/',
    url: './pages/dashboard-comment.html',
  },
  {
    path: '/signup/',
    url: './pages/signup.html',
  },
  {
    path: '/mybooks/',
    url: './pages/mybooks.html',
  },
  {
    path: '/form-result/',
    url: './pages/form-result.html'
  },
  {
    path: '/form-add/',
    url: './pages/form-add.html',
  },
  // Left View Pages
  {
    path: '/left-page-1/',
    url: './pages/left-page-1.html',
  },
  {
    path: '/left-page-2/',
    url: './pages/left-page-2.html',
  },
  // Page Loaders & Router
  {
    path: '/page-loader-template7/:user/:userId/:posts/:postId/',
    templateUrl: './pages/page-loader-template7.html',
  },
  {
    path: '/page-loader-component/:user/:userId/:posts/:postId/',
    componentUrl: './pages/page-loader-component.html',
  },
  {
    path: '/request-and-load/user/:userId/',
    async: function (routeTo, routeFrom, resolve, reject) {
      // Router instance
      var router = this;

      // App instance
      var app = router.app;

      // Show Preloader
      app.preloader.show();

      // User ID from request
      var userId = routeTo.params.userId;

      // Simulate Ajax Request
      setTimeout(function () {
        // We got user data from request
        var user = {
          firstName: 'Vladimir',
          lastName: 'Kharlampidi',
          about: 'Hello, i am creator of Framework7! Hope you like it!',
          links: [
            {
              title: 'Framework7 Website',
              url: 'http://framework7.io',
            },
            {
              title: 'Framework7 Forum',
              url: 'http://forum.framework7.io',
            },
          ]
        };
        // Hide Preloader
        app.preloader.hide();

        // Resolve route to load page
        resolve(
          {
            componentUrl: './pages/request-and-load.html',
          },
          {
            context: {
              user: user,
            }
          }
        );
      }, 1000);
    },
  },
  // Default route (404 page). MUST BE THE LAST
  {
    path: '(.*)',
    url: './pages/404.html',
  },
];

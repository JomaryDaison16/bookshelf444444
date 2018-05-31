
var token = '';
var username = '';

function login()
    {
        var username = $("#username").val();
        var password = $("#password").val();
        $.ajax({
            async: true, 
            url: 'http://127.0.0.1:5050/login',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({
                'username': username,
                'password': password
                    }),
            type: "POST",
            dataType: "json",
            crossDomain: true,
            headers: {
                'Authorization' : 'Basic ' + btoa(username + ':' + password)
                      },

        error: function (data) {
          console.log(data)
        },

        success: function (data)  {
            alert(username+ " enjoy")
            localStorage.setItem('token', data.token);
            localStorage.setItem('username', data.username);
            window.location.assign('/logged.html');
        },

        complete: function (jqXHR) {
                      if (jqXHR.status == '401') {
                          console.log(jqXHR.status)
         }}
    });
  }

function profile2(){
      var username = localStorage.getItem('username');
      $.ajax({
          url: 'http://127.0.0.1:5050/user/info/'+username ,
          type: "GET",
          contentType: 'application/json; charset=utf-8',
          dataType: "json",
            
          success: function(data){

            // user info in userprofile.html
            $("#name").html('');
            $("#name").append('<h1>'+data.first_name+' '+data.last_name+'</h1>');
            $("#contact").html('');
            $("#contact").append(data.contact_number)
            $("#contact").html('');
            $("#contact").append(data.contact_number)
            // userName in side pannel
            $("#showuser").html('');
            $("#showuser").append(data.username)

          },
          
          error: function(data){
              alert("user is not found");
          }
     });
}


function register() {
  var fname = $("#first_name").val();
  var lname = $("#last_name").val();
  var contact_number = $("#contact_number").val();
  var birth_date = $("#birth_date").val();
  var gender = $("#gender").val();
  var username = $("#username").val();
  var password = $("#password").val();
  var address = $("#address").val();
  $.ajax({
    url: "https://bookshelfv2-api.herokuapp.com/signup",
    contentType: 'application/json; charset=utf-8',
    
    data: JSON.stringify({
      'first_name': fname,
      'last_name': lname,
      'contact_number': contact_number,
      'birth_date': birth_date,
      'gender': gender,
      'username': username,
      'password': password,
      'address': address
    }),
    method: "POST",
    dataType: "json",
    crossDomain: true,
    success: function(resp) {
      console.log("success");
      move(64,48);
      alert("Registered successfully!");
      window.location.replace("upload.html");
    },
    error: function (e) {
      console.log('error');
    }
  })
}

// search by {authorname, ISBN , or title of book}
function search1(){
  var types = $("#booktype").val();
  var isbn = $("#isbn1").val();
  var title = $("#titleni").val();
  var author_name = $("#author_name").val();
 
  if (types == "isbn_"){ 
    addbookisbn(isbn);
  } else if (types == "title_"){
    alert(title+ " absdbabsdbasd")
    addbooktitle(title);
  } else if (types == "author_")
    addbookauthor(author_name);
}

function addbook()
  {
    var price = '500';
    var method = $("#method").val();
    var quantity = $("#quantity").val();
    var isbn = localStorage.getItem('isbn');
    var description = localStorage.getItem('description');
    var publisher_name = localStorage.getItem('publisher_name');
    var title = localStorage.getItem('title');
    var author_name = localStorage.getItem('author_name');
    var book_cover = localStorage.getItem('book_cover');
    var year = localStorage.getItem('year');
    var tokens = localStorage.getItem('token');
    var username = localStorage.getItem('username');
    var fiction =['Adventure', 'Action', 'Drama', 'Horror', 'Mystery', 'Mythology'];
    var nonFiction = ['Biography', 'Essay', 'Journalism', 'Personal Narrative', 'Reference Book', 'Speech'];
    var academics = ['English', 'History', 'Math', 'Science'];
    alert(tokens);
    var category = "";
    var genre1 = $("#genre").val();
     if (fiction.includes(genre1)) {
              var category= "Fiction";
            } else if (nonFiction.includes(genre1)) {
              var category= "Non-Fiction";
            }
            else {
              var category= "Educational";
            }

    var selectedchecktxt = $('ul input:checked').map(function(){
   return $(this).next('i').text();
      }).get();

    $.ajax({    
        async: true, 
        url: 'http://127.0.0.1:5050/user/addbook',
        contentType: 'application/json; charset=utf-8',
        headers: {'x-access-token': tokens},
        method: "POST",
        dataType: "json",
        crossDomain: true,
        data: JSON.stringify({
            

            "isbn": isbn,
            "title": title,
            "publisher_name": publisher_name, 
            "year": year, 
            "current_user": username ,
            "author_name": author_name,
            "quantity": $("#quantity").val(),
            "method": selectedchecktxt,
            "price": price,
            "book_cover": book_cover,
            "genre": $("#genre").val(),
            "category": category,
            "description": description
          }),

        success: function(data) {
        console.log(data);
        alert(title+ " book is added")
        },
        
        error: function (data) {
        console.log(data);
        }
    })
}

function addbookisbn(isbn){
    var tokens = localStorage.getItem('token');
    alert(isbn)
    
    $.ajax({
        url: 'http://127.0.0.1:5050/mobile/user/isbn_check/'+isbn,
        contentType: 'application/json; charset=utf-8',
        method: "GET",
        crossDomain: true,
        headers: {'x-access-token': tokens},
        success:function(data){
            alert(data[0]);
            var isbn = localStorage.setItem('isbn', data[0]['isbn']);
            $("#author_name").html('');
            $("#author_name").append('<h1>'+data[0]['author_name']+'</h1>');
            $("#title").html('');
            $("#title").append(data[0]['title']);
            $("#cover").html('');
            $("#cover").append("<img src='"+ data[0]['book_cover']+"'/>");
            $("#publisher_name").html('');
            $("#publisher_name").append(data[0]['publishers'])

            var description = localStorage.setItem('description', data[0]['description']);
            var publisher_name = localStorage.setItem('publisher_name', data[0]['publishers']);
            var title = localStorage.setItem('title', data[0]['title']);
            var author_name = localStorage.setItem('author_name', data[0]['author_name']);
            var book_cover = localStorage.setItem('book_cover', data[0]['book_cover']);
            var year = localStorage.setItem('year', data[0]['year']);          
        },

    });
}


function addbookauthor(author_name){
  var tokens = localStorage.getItem('token');
  alert(author_name)

    $.ajax({
      url: 'http://127.0.0.1:5050/mobile/user/author_check/'+author_name,
      contentType: 'application/json; charset=utf-8',
      mothod: "GET",
      crossDomain: true,
      headers: {'x-access-token': tokens},
      success: function(data){
                  
            $("#author_name").html('');
            $("#author_name").append('<h1>'+data[0]['author_name']+'</h1>');
            $("#title").html('');
            $("#title").append(data[0]['title']);
            $("#cover").html('');
            $("#cover").append("<img src='"+ data[0]['book_cover']+"'/>");
            $("#publisher_name").html('');
            $("#publisher_name").append(data[0]['publishers']);

            var isbn = localStorage.setItem('isbn', data[0]['isbn']);
            var description = localStorage.setItem('description', data[0]['description']);
            var publisher_name = localStorage.setItem('publisher_name', data[0]['publishers']);
            var title = localStorage.setItem('title', data[0]['title']);
            var author_name = localStorage.setItem('author_name', data[0]['author_name']);
            var book_cover = localStorage.setItem('book_cover', data[0]['book_cover']);
            var year = localStorage.setItem('year', data[0]['year']);
      },
  });
}

function rate() {
    $.ajax(
        {
            url: "https://bookshelfv2-api.herokuapp.com/user-rate/<int:user_idRatee>",
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify({
                'rate': $("#rateYo").rateYo("rate"),
            }),
            type: "POST",
            dataType: "json",
            error: function (data) {
            },
            success: function (data) {
                if (resp.status == 'ok') {
                    alert("Thank you for your rating!");
                }
                else {
                    alert("ERROR");
                }
            }
        });
}


var x = document.getElementById("login-alert");

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        x.innerHTML = "Geolocation is not supported by this browser.";
    }
}
function showPosition(position) {
    var key = "AIzaSyC8JFlPDHhx9WPBTqjArOYbXqLaULPvs8c"
    var latlon = position.coords.latitude + "," + position.coords.longitude;
    var ajax = $.ajax({
    type: "POST",
    url: "https://www.googleapis.com/geolocation/v1/geolocate?key=key",
    // data: JSON.stringify({current_user: username,latitude: position.coords.latitude, longitude: position.coords.longitude}),
    dataType: "json",
    contentType: "application/json; charset=UTF-8",
    success : function(data) {
              
            },
    });
}

function showError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            x.innerHTML = "User denied the request for Geolocation."
            break;
        case error.POSITION_UNAVAILABLE:
            x.innerHTML = "Location information is unavailable."
            break;
        case error.TIMEOUT:
            x.innerHTML = "The request to get user location timed out."
            break;
        case error.UNKNOWN_ERROR:
            x.innerHTML = "An unknown error occurred."
            break;
    }
}


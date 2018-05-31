


function signup0(){
        var fname = $("#first_name").val();
        var lname = $("#last_name").val();
        var contact_number = $("#contact_number").val();
        var birthdate = $("#birthdate").val();
        var gender = $("#gender").val();
        var username = $("#username").val();
        var password = $("#password").val();
        var address = $("#address").val();
        $.ajax({
          url: "https://nameless-cove-48814.herokuapp.com/signup",
          contentType: 'application/json; charset=utf-8',
          data: JSON.stringify({
            'first_name': fname,
            'last_name': lname,
            'contact_number': contact_number,
            'birthdate': birthdate,
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
            alert("Registered successfully!");
          },
          error: function (e) {
            alert(birthdate)
            console.log('error');
          }
        });
    }

function login()
    {
        var username = $("#username").val();
        var password = $("#password").val();
        $.ajax({
            async: true, 
            url: 'https://desolate-basin-69053.herokuapp.com/login',
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
            alert(username+ " logged innnnnnnn")
            localStorage.setItem('token', data.token);
            localStorage.setItem('username', username);
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
      alert(username+ "wala or naa?");
      
      $.ajax({
          url: 'https://desolate-basin-69053.herokuapp.com/user/info/'+username ,
          type: "GET",
          contentType: 'application/json; charset=utf-8',
          dataType: "json",
            
          success: function(data){
            alert(data.user.username)
            // user info in userprofile.html
            $("#name").html('');
            $("#name").append('<h1>'+data.user.first_name+' '+data.user.last_name+'</h1>');
            $("#contact").html('');
            $("#contact").append(data.user.contact_number)
            $("#contact").html('');
            $("#contact").append(data.user.contact_number)
            // userName in side pannel
            $("#showuser").html('');
            $("#showuser").append(data.user.username)
            $("#bday").html('');
            $("#bday").append(data.user.birth_date)
            $("#gender").html('');
            $("#gender").append(data.user.gender)
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
    var index = localStorage.getItem('index');
    var isbn = JSON.parse(localStorage.getItem("stire"))[index]['isbn'];
    var description = JSON.parse(localStorage.getItem("stire"))[index]['description'];
    var publisher_name = JSON.parse(localStorage.getItem("stire"))[index]['publishers'];
    var title = JSON.parse(localStorage.getItem("stire"))[index]['title'];
    var author_name = JSON.parse(localStorage.getItem("stire"))[index]['author_name'];
    var book_cover = JSON.parse(localStorage.getItem("stire"))[index]['book_cover'];
    var year = JSON.parse(localStorage.getItem("stire"))[index]['year'];
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
        url: 'https://desolate-basin-69053.herokuapp.com/user/addbook',
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

    
    
    $.ajax({
        url: 'https://desolate-basin-69053.herokuapp.com/mobile/user/isbn_check/'+isbn,
        contentType: 'application/json; charset=utf-8',
        method: "GET",
        crossDomain: true,
        headers: {'x-access-token': tokens},
        success:function(data){


            loop = [];
            $('#earl').html('');
            var e = 0;
            for(i=0; i<data.length; i++){
              $('#earl').append(printhher(data[i]['title'], data[i]['book_cover'], data[i]['author_name'], parseInt(i)));
             e = e + 1;
            }
            for(i=0; i<data.length; i++){
              var bb = {'author_name': data[i]['author_name'],'isbn':data[i]['isbn'], 'title': data[i]['title'], 'book_cover': data[i]['book_cover'], 'publishers': data[i]['publishers'], 'description':data[i]['description'], 'year':data[i]['year'], 'types':data[i]['types'], 'book_id':data[i]['book_id'] };
              loop.push(bb);
            }

            localStorage.setItem("stire", JSON.stringify(loop));

            console.log(JSON.parse(localStorage.getItem("stire"))[0]);
            // alert(data[0]);
            // var isbn = localStorage.setItem('isbn', data[0]['isbn']);
            // $("#author_name").html('');
            // $("#author_name").append('<h1>'+ author_name +'</h1>');
            // $("#title").html('');
            // $("#title").append(title);
            // $("#cover").html('');
            // $("#cover").append("<img src='"+ book_cover +"'/>");
            // $("#publisher_name").html('');
            // $("#publisher_name").append(publisher_name)

            // var description = localStorage.setItem('description', data[0]['description']);
            // var publisher_name = localStorage.setItem('publisher_name', data[0]['publishers']);
            // var title = localStorage.setItem('title', data[0]['title']);
            // var author_name = localStorage.setItem('author_name', data[0]['author_name']);
            // var book_cover = localStorage.setItem('book_cover', data[0]['book_cover']);
            // var year = localStorage.setItem('year', data[0]['year']);          
        },

    });
}

function printhher(n,m,o,pasa){

  return '<div class="card-header">'+
        '<div class="demo-facebook-name" id="title">'+n+'</div>'+
      '</div>'+
      '<div id="cover"><img src="'+m+'"/></div>'+
      '<div class="card-content card-content-padding">'+

        '<p id="author_name">'+o+'</p>'+
        '<p class="likes">Rating: 4.5/5</p>'+
      '</div>'+
      '<div class="card-footer">'+
      '<a onclick="get_index(\''+pasa+'\');" href="/form-add/" class="link right" name="\''+pasa+'\'" id="myform1" value="\''+pasa+'\'" >Add Book</a>'+
      '</div>';
}
function get_index(pasa){
  $("a").click(function() {
    var fired_button = $(this).val();
    var index_set = localStorage.setItem('index', pasa);
  });
}



function addbooktitle(title){
  var tokens = localStorage.getItem('token');
  alert(title)

    $.ajax({
      url: 'https://desolate-basin-69053.herokuapp.com/mobile/user/title_check/'+title,
      contentType: 'application/json; charset=utf-8',
      mothod: "GET",
      crossDomain: true,
      headers: {'x-access-token': tokens},
      success: function(data){
            loop = [];
            $('#earl').html('');
            var e = 0;
            for(i=0; i<data.length; i++){
              $('#earl').append(printhher(data[i]['title'], data[i]['book_cover'], data[i]['author_name'], parseInt(i)));
             e = e + 1;
            }
            /*$("#author_name").html('');
            $("#author_name").append('<h1>'+data[0]['author_name']+'</h1>');
            $("#title").html('');
            $("#title").append(data[0]['title']);
            $("#cover").html('');
            $("#cover").append("<img src='"+ data[0]['book_cover']+"'/>");
            $("#publisher_name").html('');
            $("#publisher_name").append(data[0]['publishers']);*/

            for(i=0; i<data.length; i++){
              var bb = {'author_name': data[i]['author_name'],'isbn':data[i]['isbn'], 'title': data[i]['title'], 'book_cover': data[i]['book_cover'], 'publishers': data[i]['publishers'], 'description':data[i]['description'], 'year':data[i]['year'], 'types':data[i]['types'], 'book_id':data[i]['book_id'] };
              loop.push(bb);
            }

            localStorage.setItem("stire", JSON.stringify(loop));

            console.log(JSON.parse(localStorage.getItem("stire"))[0]);

            /*var isbn = localStorage.setItem('isbn', data[0]['isbn']);
            var description = localStorage.setItem('description', data[0]['description']);
            var publisher_name = localStorage.setItem('publisher_name', data[0]['publishers']);
            var title = localStorage.setItem('title', data[0]['title']);
            var author_name = localStorage.setItem('author_name', data[0]['author_name']);
            var book_cover = localStorage.setItem('book_cover', data[0]['book_cover']);
            var year = localStorage.setItem('year', data[0]['year']);*/
      },
      error: function(data){
        alert(data)
      },
  });
}

function addbookauthor(author_name){
  var tokens = localStorage.getItem('token');
  alert(author_name)

    $.ajax({
      url: 'https://desolate-basin-69053.herokuapp.com/mobile/user/author_check/'+author_name,
      contentType: 'application/json; charset=utf-8',
      mothod: "GET",
      crossDomain: true,
      headers: {'x-access-token': tokens},
      success: function(data){


            loop = [];
            $('#earl').html('');
            var e = 0;
            for(i=0; i<data.length; i++){
              $('#earl').append(printhher(data[i]['title'], data[i]['book_cover'], data[i]['author_name'], parseInt(i)));
             e = e + 1;
            }
            for(i=0; i<data.length; i++){
              var bb = {'author_name': data[i]['author_name'],'isbn':data[i]['isbn'], 'title': data[i]['title'], 'book_cover': data[i]['book_cover'], 'publishers': data[i]['publishers'], 'description':data[i]['description'], 'year':data[i]['year'], 'types':data[i]['types'], 'book_id':data[i]['book_id'] };
              loop.push(bb);
            }

            localStorage.setItem("stire", JSON.stringify(loop));

            console.log(JSON.parse(localStorage.getItem("stire"))[0]);
            // $("#author_name").html('');
            // $("#author_name").append('<h1>'+data[0]['author_name']+'</h1>');
            // $("#title").html('');
            // $("#title").append(data[0]['title']);
            // $("#cover").html('');
            // $("#cover").append("<img src='"+ data[0]['book_cover']+"'/>");
            // $("#publisher_name").html('');
            // $("#publisher_name").append(data[0]['publishers']);

            // var isbn = localStorage.setItem('isbn', data[0]['isbn']);
            // var description = localStorage.setItem('description', data[0]['description']);
            // var publisher_name = localStorage.setItem('publisher_name', data[0]['publishers']);
            // var title = localStorage.setItem('title', data[0]['title']);
            // var author_name = localStorage.setItem('author_name', data[0]['author_name']);
            // var book_cover = localStorage.setItem('book_cover', data[0]['book_cover']);
            // var year = localStorage.setItem('year', data[0]['year']);
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


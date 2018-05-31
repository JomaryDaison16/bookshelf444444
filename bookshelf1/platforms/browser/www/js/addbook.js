function addbook(form){

    xhr = new XMLHttpRequest();
    var url = "http://127.0.0.1:5000/user/addbook";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function () { 
        if (xhr.readyState == 4 && xhr.status == 200) {
            var json = JSON.parse(xhr.responseText);
            // console.log(json.form.id.value +", " + json.form.acc_type.value + ", " + json.form.email.value + ", " + json.form.pass.value);
        }
    }
    var json =JSON.stringify({
        "title": form.title.value,
        "publisher_name":form.publisher_name.value, 
        "year":form.year.value, 
        "edition":form.edition.value,
        "types":form.types.value,
        "author_fname":form.author_fname.value,
        "author_lname":form.author_lname.value,
        "isbn":form.isbn.value,
        // "categories":form.categories.value,
        // "descrip":form.descrip.value,
        // "selltype":form.selltype.value,
        // "bookprice":form.bookprice.value,
    });
    console.log(json)
    xhr.send(json);

    alert("Thanks " + form.booktitle.value  + "! Added.");
       

}
function changeUp(name, filename){
    return '<p id="showname">'+name+'</p>'+
		'<img src="'+filename+'"style="width: 150px; height:150px; border-radius: 50%;">';
}

function editprof(){
	var form = new FormData();
    form.append('avatar', $('input[name="avatar"]')[0].files[0]);

    $.ajax({
    		type: 'POST',
            url: '"http://127.0.0.1:5000/<userid>/profpic',
            data: form,
            cache: false,
            contentType: false,
            processData: false,
            async: false,
            success: function(resp) {
            	console.log(resp.msg);
            	$('#showinfo').html("");
                $('#showinfo').append(changeUp(resp.name, resp.filename));
              window.location.replace("interest.html");
            },
    });

}

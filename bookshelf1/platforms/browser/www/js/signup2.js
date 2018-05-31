var slideIndex = 1;
showSlides(slideIndex);

// Next/previous controls
function plusSlides(n) {
  showSlides(slideIndex += n);
}

// Thumbnail image controls
function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  var i;
  var slides = document.getElementsByClassName("mySlides");
  var dots = document.getElementsByClassName("dot");
  if (n > slides.length) {slideIndex = 1}
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";
  }
  slides[slideIndex-1].style.display = "block";
} 
function move(n,m) {
  var elem = document.getElementById("progBar");   
  var width = m;
  var id = setInterval(frame, 10);
  function frame() {
    if (width >= n) {
      clearInterval(id);
    } else {
      width++; 
      elem.style.width = width + '%'; 
      document.getElementById("demo").innerHTML = width * 1  + '% COMPLETE';
    }
  }
}
function dmove(n,m) {
  var elem = document.getElementById("progBar");   
  var width = m;
  var id = setInterval(frame, 10);
  function frame() {
    if (width <= n) {
      clearInterval(id);
    } else {
      width--; 
      elem.style.width = width + '%'; 
      document.getElementById("demo").innerHTML = width * 1  + '% COMPLETE';
    }
  }
}

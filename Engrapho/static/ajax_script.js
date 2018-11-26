var animalContainer = document.getElementById(NAME);
var btn = document.getElementByClassName("btn-search");

btn.addEventListener("click", function() {
	//Add code to call the data needed
	var search = document.getElementById('search').value;
	var ourRequest = new XMLHttpRequest();
	ourRequest.open('GET', LINK);
	ourRequest.onload = function() {
		var ourData = JSON.parse(ourRequest.responseText);
		renderHTML(ourData);
	};
	ourRequest.send();
});

function renderHTML(data) {
	var htmlString = '';

	for (i=0; i< data.length; i++){
		htmlString += "<p>" + data[i] + "</p>"
	}

	animalContainer.insertAdjacentHTML('beforeend', htmlstring);
}
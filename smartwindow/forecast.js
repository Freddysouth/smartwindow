var values = [0.2,1,3,2,4,5,6];
var lowmedhigh = ["low", "high", "low", "medium", "low", "medium", "low"];

function pollution(listOfValues, listOfLevel){
    console.log("Kjører")
	var i;
	for (i = 0; i < 7; i++){
		var n = i.toString();
        //document.getElementsByClassName("card-text")[i].innerHTML = listOfValues[i];
        document.getElementsByClassName("text-muted")[i].innerHTML = listOfValues[i];
        
        if (listOfLevel[i] == "low"){
            document.getElementsByClassName("card-footer")[i].id="green";
            var image = document.getElementsByClassName("card-img-top")[i];
            image.src = "images/open_brown.png"
        }
        else if (listOfLevel[i] == "medium"){
             document.getElementsByClassName("card-footer")[i].id="yellow";
            var image = document.getElementsByClassName("card-img-top")[i];
            image.src = "images/medium_brown.png"
        }
        else if (listOfLevel[i] == "high"){
            document.getElementsByClassName("card-footer")[i].id="red";
            var image = document.getElementsByClassName("card-img-top")[i];
            image.src = "images/close_brown.png"
        }
         
	}
}

pollution(values, lowmedhigh);
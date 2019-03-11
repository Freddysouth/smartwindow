//var dict = '{"pollutionValue": [12.09, 2, 90, 31, 12, 35.5, 90], "pollutionLevel": ["medium", "low", "high", "medium", "low", "high", "high"]}'

function jsonToLists(jsonFile){
    var pollutionDict = JSON.parse(jsonFile);
    pollution(pollutionDict.pollutionValue, pollutionDict.pollutionLevel);    
}
//Place pollutionValue in HTML "text-muted" and change textcolor and window image according to the pollutionLevel.

function pollution(listOfValues, listOfLevel){
	var i;
	for (i = 0; i < 7; i++){
		var n = i.toString();
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

//Days placed in "card-title" in HTML
var days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

function transformDay(dayInNumber){
    return days[dayInNumber];
}

function dateInCard(){
    var dt = new Date();
    var day = dt.getDay();
    
    for (i = 0; i < 7; i++){
        if (i == 0){
            document.getElementsByClassName("card-title")[i].innerHTML = "Today";
        }else{
            document.getElementsByClassName("card-title")[i].innerHTML = transformDay((day+i)%7);     
        }
    }
}

dateInCard();
//jsonToLists(the request that returns json object);
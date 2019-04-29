
//Place pollutionValue in HTML "pm25Value" and change textcolor and window image according to the pollutionLevel.
function pollution(listOfPM25, listOfPM10, levelPM25, levelPM10){
    var image = document.getElementsByClassName("card-img-top");
    var pm25 = document.getElementsByClassName("pm25Value");
    var pm10 = document.getElementsByClassName("pm10Value");
    
    var i;
    for (i = 0; i < 7; i++){
        pm25[i].innerHTML = Math.round(listOfPM25[i]*10)/10;
        pm10[i].innerHTML = Math.round(listOfPM10[i]*10)/10;
        
        if (levelPM25[i] == 0){
            pm25[i].id = "green";
        }else if (levelPM25[i] == 1){
            pm25[i].id = "yellow";
        }else if (levelPM25[i] == 2){
            pm25[i].id = "red";
        }
        if (levelPM10[i] == 0){
            pm10[i].id = "green";
        }else if (levelPM10[i] == 1){
            pm10[i].id = "yellow";
        }else if (levelPM10[i] == 2){
            pm10[i].id = "red";
        }
        if (levelPM25[i] < levelPM10[i]){
            image[i].src = `./static/images/${levelPM10[i]}.png`;
        }else{
            image[i].src = `./static/images/${levelPM25[i]}.png`;
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

$(document).ready(() => {
    let urlPM10 = 'predict/static/PM10' // if you want to use the continuously trained model: predict/dynamic/PM10 
    let urlPM2_5 = 'predict/static/PM2_5' // if you want to use the continuously trained model: predict/dynamic/PM2_5 
    $.get(urlPM10, (dataPM10, status) => {
        $.get(urlPM2_5, (dataPM2_5, status) => {
            pollution(dataPM2_5.predictedPollution, dataPM10.predictedPollution, dataPM2_5.descriptions, dataPM10.descriptions);
        })
    });
    dateInCard();
})
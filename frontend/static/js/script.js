// ========================== start session ========================
$(document).ready(function () {

	//drop down menu
	$('.dropdown-trigger').dropdown();

	//enable this if u have configured the bot to start the conversation. 
	//showBotTyping();
	//$("#userInput").prop('disabled', true);

	//get user ID
	const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    const userid = urlParams.get('userid');
	user_id = userid;
	const session_num = urlParams.get('n');
	
	//start a session
	if (session_num == "1"){
		send('/start_session1{"session_num":"1"}');
	} else if (session_num == "2"){
		send('/start_session_mid{"session_num":"2"}');
    } else if (session_num == "3"){
		send('/start_session_mid{"session_num":"3"}');
    } else if (session_num == "4"){
		send('/start_session_mid{"session_num":"4"}');
    } else if (session_num == "5"){
		send('/start_session_last{"session_num":"5"}');
	}
	

})

//=====================================	user enter or sends the message =====================
$(".usrInput").on("keyup keypress", function (e) {
	var keyCode = e.keyCode || e.which;

	var text = $(".usrInput").val();
	if (keyCode === 13) {

		if (text == "" || $.trim(text) == "") {
			e.preventDefault();
			return false;
		} else {
			//destroy the existing chart, if yu are not using charts, then comment the below lines
			$('.collapsible').remove();
			if (typeof chatChart !== 'undefined') { chatChart.destroy(); }

			$(".chart-container").remove();
			if (typeof modalChart !== 'undefined') { modalChart.destroy(); }



			$("#paginated_cards").remove();
			$(".suggestions").remove();
			$(".quickReplies").remove();
			$(".usrInput").blur();
			setUserResponse(text);
			send(text);
			e.preventDefault();
			return false;
		}
	}
});

$("#sendButton").on("click", function (e) {
	var text = $(".usrInput").val();
	if (text == "" || $.trim(text) == "") {
		e.preventDefault();
		return false;
	}
	else {
		//destroy the existing chart

		chatChart.destroy();
		$(".chart-container").remove();
		if (typeof modalChart !== 'undefined') { modalChart.destroy(); }

		$(".suggestions").remove();
		$("#paginated_cards").remove();
		$(".quickReplies").remove();
		$(".usrInput").blur();
		setUserResponse(text);
		send(text);
		e.preventDefault();
		return false;
	}
})

//==================================== Set user response =====================================
function setUserResponse(message) {
	var UserResponse = '<img class="userAvatar" src=' + "/img/user_picture.png" + '><p class="userMsg">' + message + ' </p><div class="clearfix"></div>';
	$(UserResponse).appendTo(".chats").show("slow");

	$(".usrInput").val("");
	scrollToBottomOfResults();
	showBotTyping();
	$(".suggestions").remove();
}

//=========== Scroll to the bottom of the chats after new message has been added to chat ======
function scrollToBottomOfResults() {

	var terminalResultsDiv = document.getElementById("chats");
	terminalResultsDiv.scrollTop = terminalResultsDiv.scrollHeight;
}

//============== send the user message to rasa server =============================================
function send(message) {
	$.ajax({

		url: "http://34.159.190.156:5005/webhooks/rest/webhook",
		type: "POST",
		contentType: "application/json",
		data: JSON.stringify({ message: message, sender: user_id }),
		success: function (botResponse, status) {
			console.log("Response from Rasa: ", botResponse, "\nStatus: ", status);

			// if user wants to restart the chat and clear the existing chat contents
			if (message.toLowerCase() == '/restart') {
				$("#userInput").prop('disabled', false);

				//if you want the bot to start the conversation after restart
				// action_trigger();
				return;
			}
			setBotResponse(botResponse);

		},
		error: function (xhr, textStatus, errorThrown) {

			if (message.toLowerCase() == '/restart') {
				// $("#userInput").prop('disabled', false);

				//if you want the bot to start the conversation after the restart action.
				// action_trigger();
				// return;
			}

			// if there is no response from rasa server
			setBotResponse("");
			console.log("Error from bot end: ", textStatus);
		}
	});
}

//=================== set bot response in the chats ===========================================
function setBotResponse(response) {

	//display bot response after 500 milliseconds
	setTimeout(function () {
		hideBotTyping();
		if (response.length < 1) {
			//if there is no response from Rasa, send  fallback message to the user
			var fallbackMsg = "I am facing some issues, please try again later!!!";

			var BotResponse = '<img class="botAvatar" src="/img/chatbot_picture.png"/><p class="botMsg">' + fallbackMsg + '</p><div class="clearfix"></div>';

			$(BotResponse).appendTo(".chats").hide().fadeIn(1000);
			scrollToBottomOfResults();
		}
		else {

			//if we get response from Rasa
			for (i = 0; i < response.length; i++) {

				//check if the response contains "text"
				if (response[i].hasOwnProperty("text")) {
					var response_text = response[i].text.split("\n")
					for (j = 0; j < response_text.length; j++){
						var BotResponse = '<img class="botAvatar" src="/img/chatbot_picture.png"/><p class="botMsg">' + response_text[j] + '</p><div class="clearfix"></div>';
						$(BotResponse).appendTo(".chats").hide().fadeIn(1000);
					}
				}

				//check if the response contains "images"
				if (response[i].hasOwnProperty("image")) {
					var BotResponse = '<div class="singleCard">' + '<img class="imgcard" src="' + response[i].image + '">' + '</div><div class="clearfix">';
					$(BotResponse).appendTo(".chats").hide().fadeIn(1000);
				}


				//check if the response contains "buttons" 
				if (response[i].hasOwnProperty("buttons")) {
					addSuggestion(response[i].buttons);
				}

				//check if the response contains "custom" message  
				if (response[i].hasOwnProperty("custom")) {

					//check if the custom payload type is "quickReplies"
					if (response[i].custom.payload == "quickReplies") {
						quickRepliesData = response[i].custom.data;
						showQuickReplies(quickRepliesData);
						return;
					}

					//check if the custom payload type is "dropDown"
					if (response[i].custom.payload == "dropDown") {
						dropDownData = response[i].custom.data;
						renderDropDwon(dropDownData);
						return;
					}

					//check of the custom payload type is "collapsible"
					if (response[i].custom.payload == "collapsible") {
						data = (response[i].custom.data);
						//pass the data variable to createCollapsible function
						createCollapsible(data);
					}
				}
			}
			scrollToBottomOfResults();
		}
	}, 500);
}

//====================================== Toggle chatbot =======================================
$("#profile_div").click(function () {
	$(".profile_div").toggle();
	$(".widget").toggle();
});

//====================================== DropDown ==================================================
//render the dropdown messageand handle user selection
function renderDropDwon(data) {
	var options = "";
	for (i = 0; i < data.length; i++) {
		options += '<option value="' + data[i].value + '">' + data[i].label + '</option>'
	}
	var select = '<div class="dropDownMsg"><select class="browser-default dropDownSelect"> <option value="" disabled selected>Choose your option</option>' + options + '</select></div>'
	$(".chats").append(select);

	//add event handler if user selects a option.
	$("select").change(function () {
		var value = ""
		var label = ""
		$("select option:selected").each(function () {
			label += $(this).text();
			value += $(this).val();
		});

		setUserResponse(label);
		send(value);
		$(".dropDownMsg").remove();
	});
}

//====================================== Suggestions ===========================================

function addSuggestion(textToAdd) {
	setTimeout(function () {
		$('.usrInput').attr("disabled",true);
		$(".usrInput").prop('placeholder', "Use one of the buttons to answer.");
		var suggestions = textToAdd;
		var suggLength = textToAdd.length;
		$(' <div class="singleCard"> <div class="suggestions"><div class="menu"></div></div></diV>').appendTo(".chats").hide().fadeIn(1000);
		// Loop through suggestions
		for (i = 0; i < suggLength; i++) {
			$('<div class="menuChips" data-payload=\'' + (suggestions[i].payload) + '\'>' + suggestions[i].title + "</div>").appendTo(".menu");
		}
		scrollToBottomOfResults();
	}, 1000);
}

// on click of suggestions, get the value and send to rasa
$(document).on("click", ".menu .menuChips", function () {
	$('.usrInput').attr("disabled",false);
	$(".usrInput").prop('placeholder', "Type a message...");
	var text = this.innerText;
	var payload = this.getAttribute('data-payload');
	console.log("payload: ", this.getAttribute('data-payload'))
	setUserResponse(text);
	send(payload);

	//delete the suggestions once user click on it
	$(".suggestions").remove();

});

//====================================== functions for drop-down menu of the bot  =========================================

//fullscreen function to toggle fullscreen.
$("#fullscreen").click(function () {
	if ($('.widget').width() == 350) {
		// This determines the width and height of the window when opened in browser on a laptop
		$('.widget').css("width" , "98%");
		$('.widget').css("height" , "100%");
	} else {
		$('.widget').css("width" , "350px");
		$('.widget').css("height" , "100%");
	}
});

//====================================== Quick Replies ==================================================

function showQuickReplies(quickRepliesData) {
	var chips = ""
	for (i = 0; i < quickRepliesData.length; i++) {
		var chip = '<div class="chip" data-payload=\'' + (quickRepliesData[i].payload) + '\'>' + quickRepliesData[i].title + '</div>'
		chips += (chip)
	}

	var quickReplies = '<div class="quickReplies">' + chips + '</div><div class="clearfix"></div>'
	$(quickReplies).appendTo(".chats").fadeIn(1000);
	scrollToBottomOfResults();
	const slider = document.querySelector('.quickReplies');
	let isDown = false;
	let startX;
	let scrollLeft;

	slider.addEventListener('mousedown', (e) => {
		isDown = true;
		slider.classList.add('active');
		startX = e.pageX - slider.offsetLeft;
		scrollLeft = slider.scrollLeft;
	});
	slider.addEventListener('mouseleave', () => {
		isDown = false;
		slider.classList.remove('active');
	});
	slider.addEventListener('mouseup', () => {
		isDown = false;
		slider.classList.remove('active');
	});
	slider.addEventListener('mousemove', (e) => {
		if (!isDown) return;
		e.preventDefault();
		const x = e.pageX - slider.offsetLeft;
		const walk = (x - startX) * 3; //scroll-fast
		slider.scrollLeft = scrollLeft - walk;
	});

}

// on click of quickreplies, get the value and send to rasa
$(document).on("click", ".quickReplies .chip", function () {
	var text = this.innerText;
	var payload = this.getAttribute('data-payload');
	console.log("chip payload: ", this.getAttribute('data-payload'))
	setUserResponse(text);
	send(payload);

	//delete the quickreplies
	$(".quickReplies").remove();

});

//======================================bot typing animation ======================================
function showBotTyping() {

	var botTyping = '<img class="botAvatar" id="botAvatar" src="/img/chatbot_picture.png"/><div class="botTyping">' + '<div class="bounce1"></div>' + '<div class="bounce2"></div>' + '<div class="bounce3"></div>' + '</div>'
	$(botTyping).appendTo(".chats");
	$('.botTyping').show();
	scrollToBottomOfResults();
}

function hideBotTyping() {
	$('#botAvatar').remove();
	$('.botTyping').remove();
}

//====================================== Collapsible =========================================

// function to create collapsible,
// for more info refer:https://materializecss.com/collapsible.html
function createCollapsible(data) {
	//sample data format:
	//var data=[{"title":"abc","description":"xyz"},{"title":"pqr","description":"jkl"}]
	list = "";
	for (i = 0; i < data.length; i++) {
		item = '<li>' +
			'<div class="collapsible-header">' + data[i].title + '</div>' +
			'<div class="collapsible-body"><span>' + data[i].description + '</span></div>' +
			'</li>'
		list += item;
	}
	var contents = '<ul class="collapsible">' + list + '</uL>';
	$(contents).appendTo(".chats");

	// initialize the collapsible
	$('.collapsible').collapsible();
	scrollToBottomOfResults();
}

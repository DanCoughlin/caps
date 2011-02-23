$(document).ready(function() {	

//###################### MODAL DIALOG JS #########################
	//select all the a tag with name equal to modal
	$('a[name=modal]').click(function(e) {
		//Cancel the link behavior
		e.preventDefault();
		//Get the A tag
		var a_href = $(this).attr('href');

		///blueJ/info/a_id
		var a_id = $(this).attr('id');
		$.ajax({	
			cache: false,
			url: '/appinfo/' + a_id + "/",
			success: displayInfo 
		});
		//Get the screen height and width
		var maskHeight = $(document).height();
		var maskWidth = $(window).width();
	
		//Set height and width to mask to fill up the whole screen
		$('#mask').css({'width':maskWidth,'height':maskHeight});
		
		//transition effect		
		$('#mask').fadeIn(1000);	
		$('#mask').fadeTo("slow",0.8);	
	
		//Get the window height and width
		var winH = $(window).height();
		var winW = $(window).width();
              
		//Set the popup window to center
		$(a_href).css('top',  winH/2-$(a_href).height()/2);
		$(a_href).css('left', winW/2-$(a_href).width()/2);
	
		//transition effect
		$(a_href).fadeIn(2000); 
	
	});
	
	//if close button is clicked
	$('.window .close').click(function (e) {
		//Cancel the link behavior
		e.preventDefault();
		$('#mask, .window').hide();
	});		
	
	//if mask is clicked
	$('#mask').click(function () {
		$(this).hide();
		$('.window').hide();
	});			

	

});

function displayInfo (data) {
	//alert(data);
	var json = $.parseJSON(data);
	//var hrefStr = "<a href=\"/site_media/collections/" + cdParts[1] + "/\" target=\"_new\">" + cdParts[1] + "</a>";
	$('#appTitle').html(json.appInfo.name);
	var appInfoStr = "Department: <b>" + json.appInfo.unit + "</b><br />";
	appInfoStr += "Building: <b>" + json.appInfo.building + "</b><br />";
	appInfoStr += "Opp room: <b>" + json.appInfo.opp_room + "</b><br />";
	appInfoStr += "Contact name: <b>" + json.appInfo.contact_name + "</b><br />";
	appInfoStr += "Contact email: <b>" + json.appInfo.contact_email + "</b><br />";

	for (var i in json.appInfo.questions)
	{
		// emtpy b.c. of the way python returns the extra space
		// look at appinfo.html
		if (json.appInfo.questions[i].question == "holding") {
			break;
		}
		var index = parseInt(i)+1;
		appInfoStr += "<p><span class=\"note\">" + index  + ") "+ json.appInfo.questions[i].question; 
		appInfoStr += "</span><br />- <b>" + json.appInfo.questions[i].choice + "</b></p>";
	}
	
	$('#appInfo').html(appInfoStr);
}

function deleteApp (appId, appName) {
	if (confirm('Are you sure you would like to delete: '+appName+'?')) {
		$.ajax({	
			url: '/delete/' +appId + "/",
			success: removeApp 
		});
	}
	return false;

}

function removeApp(data) {
	//var json = $.parseJSON(data);
	elemId = "#row_"+ data;
	$(elemId).remove();
}

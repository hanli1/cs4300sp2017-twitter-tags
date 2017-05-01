triggered = false;

$( document ).ready(function() {
  $("#search-button").click(send_search_query);
  $("#user-selection-input").on('keyup', function (e) {
    // if (e.keyCode == 13) {
    //   send_search_query();
    // }
  });
  $("#tag-selection-dropdown").blur(function() {
      console.log("hid");
      if(!triggered)
        hide_dropdown();
      else
        triggered = false;
  });
  $("#tag-selection-placeholder").click(function() {
      show_dropdown();
  });
  


  function show_dropdown(){
    $("#tag-selection-dropdown").css('z-index', 3000);
    $("#tag-selection-dropdown").children().each(function () {
      if($(this).attr("tag") != "selected")
        $(this).show();
    });
  }
  function hide_dropdown(){
    var seen = false;

    var children = $("#tag-selection-dropdown").children();
    for(i = 0; i < children.length; i++){
      if(!seen){
        seen = true;
        continue;
      }
      $(children[i]).hide();
    }
  }

  function send_search_query(){
    $("#search-button").blur();
    // on search button click send query to django backend
    data = { 
        user_query: $("#user-selection-input").val(), 
        tags: get_query_tags(),
        user_type: $("#user-type-selection-input").val()
    };
    $.get('/api/search', data, function(response){
      var results = response["results"];
      $("#results").empty();
      for(i = 0; i < results.length; i++){
          result = results[i];
          var newUserResult = $(".user-result-template").eq(0).clone();
          newUserResult.find(".user-image").attr("src", result.profile_picture);
          newUserResult.find(".user-name").text(result.name);
          newUserResult.find(".user-handle-link").text("@" + result.twitter_handle);
          newUserResult.find(".user-handle-link").attr("href","https://twitter.com/" + result.twitter_handle);
          newUserResult.find(".user-cosine-similarity").text((result.cosine_similarity * 100).toFixed(2) + "% similarity");
          newUserResult.find(".user-common-words").text(result.top_words_in_common.join(", "));
          var globalCommonWordsDiv = newUserResult.find(".user-common-words");
          var numTagKeys = 0;
          for (var tagKey in result.top_tag_words_in_common) {
            if (result.top_tag_words_in_common.hasOwnProperty(tagKey)) {
                var currentTagWords = result.top_tag_words_in_common[tagKey].join(", ");
                $("<div class='user-common-words-wrapper'><strong>Top " + tagKey + " Words in Common: </strong>" +
                    "<span class='user-common-words'>" + currentTagWords + "</span> </div>").insertAfter(
                    globalCommonWordsDiv);
                numTagKeys = numTagKeys + 1;
            }
          }
          newUserResult.css("height", 110 + numTagKeys * 50);
          newUserResult.find(".user-image").css("height", 110 + numTagKeys * 50);
          newUserResult.find(".user-image-wrapper").css("width", 110 + numTagKeys * 50);
          newUserResult.find(".user-info-wrapper").css("width", String(78 - numTagKeys * 10) + "%");
          newUserResult.css("display", "block");
          $("#results").append(newUserResult);
      }
      if(results.length == 0){
        $("#results").append('<div style="text-align: center">No results found</div>');
      }
    });
  }

  // retrieves the tags that the user has selected
  function get_query_tags(){
    tags = [];
    $('#tags-container').children().each(function () {
        if($(this).is(':visible')){
          tag = $(this).html().split("<")[0];
          tags.push(tag);
          tags.push($(this).attr("tag"));
        }
    });
    return tags;
  }


  // retrieves all the users and set up autocomplete
  $.getJSON('/api/get_users_handles', {foo: 'bar'}, function(data, jqXHR){
      // do something with response
      users = data["suggestions"];
      $('#user-selection-input').autocomplete({
        lookup: users,
        lookupLimit: 5,
        autoSelectFirst: true,
        onSelect: function (suggestion) {
            // Display information about the selected user
            console.log(suggestion.value);
            var suggestion_components = suggestion.value.split(" ");
            var twitter_handle = suggestion_components[suggestion_components.length - 1];
            var twitter_handle = twitter_handle.substring(2, twitter_handle.length - 1);
            $.getJSON('/api/get_user_info', {twitter_handle: twitter_handle}, function(data, jqXHR){
                var user_data = data.user_data;
                var user_tags = data.user_tags;
                $("#user_name").text(user_data.name);
                $("#user_handle").attr("href","https://twitter.com/" + user_data.twitter_handle);
                $("#user_handle").text("@" + user_data.twitter_handle);
                $("#user_profile_picture").attr("src", user_data.profile_image);
                $("#user_name").text(user_data.name);
                var user_tags_str = "";
                for(var i = 0; i < user_tags.length; i++) {
                    user_tags_str = user_tags_str + user_tags[i] + ", ";
                }
                user_tags_str = user_tags_str.substring(0, user_tags_str.length - 2);
                $("#user_tags").text(user_tags_str);
                // $("#user_information_wrapper").show();
                $("#user-query-result").show()
            });
        }
      });
  });


  // get all the tags available and set up autocomplete
  $.getJSON('/api/get_tag_labels', {foo: 'bar'}, function(data, jqXHR){
      // do something with response
      tag_labels = data["suggestions"];
      var container = $("#tag-selection-dropdown");
      for(i = 0; i < tag_labels.length; i++) (function(i){
        var tag_label = tag_labels[i]["value"];
        var element = $("<div></div>");
        element.addClass("tag-selection-row");
        element.text(tag_label);
        var plus = $("<button>+</button>");
        plus.css({ 'color': "green" });
        var minus = $("<button>-</button>");
        minus.css({ 'color': "red" });
        var buttons = $("<div></div>");
        buttons.addClass("dropdown-buttons-container");
        plus.addClass("dropdown-buttons");
        minus.addClass("dropdown-buttons");
        buttons.append(plus);
        buttons.append(minus);

        plus.mousedown(function(){
          add_chip(tag_label, true);
          element.attr("tag", "selected");
          hide_dropdown();
        });
        minus.mousedown(function(){
          add_chip(tag_label, false);
          element.attr("tag", "selected");
          hide_dropdown();
        });
        element.append(buttons);
        element.hide();
        container.append(element);
      })(i);
  });

  function add_chip(value, positive){
    var span = $("<span class=\"closebtn\">&times;</span>");
    var chip = $("<div>" + "</div>").hide();
    chip.append(value);
    chip.append(span);
    if(positive){
      chip.addClass("chip-positive");
      chip.attr("tag", "positive");
    }
    else{
      chip.addClass("chip-negative");
      chip.attr("tag", "negative");
    }
    span.click(function(){
      chip.hide();
      $("#tag-selection-dropdown").children().each(function () {
        console.log($(this).text())
        if($(this).text().replace("+-", "") == value)
          $(this).attr("tag", "");
      });
    });
    chip.addClass("shadow");
    chip.appendTo($("#tags-container")).fadeIn(200);
    // $("#tag-selection-input").val("");
  }


});
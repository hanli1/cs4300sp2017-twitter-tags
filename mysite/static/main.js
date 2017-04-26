$( document ).ready(function() {
  $("#search-button").click(send_search_query);
  $("#user-selection-input").on('keyup', function (e) {
    if (e.keyCode == 13) {
      send_search_query();
    }
  });
});

function send_search_query(){
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
        var newUserResult = $(".user-result").eq(0).clone();
        newUserResult.find(".user-image").attr("src", result.profile_picture);
        newUserResult.find(".user-name").text(result.name);
        newUserResult.find(".user-handle-link").text("@" + result.twitter_handle);
        newUserResult.find(".user-handle-link").attr("href","https://twitter.com/" + result.twitter_handle);
        newUserResult.find(".user-cosine-similarity").text((result.cosine_similarity * 100).toFixed(2) + "% similarity");
        newUserResult.find(".user-common-words").text(result.top_words_in_common.join(", "));
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
              $("#user_information_wrapper").show();
          });
      }
    });
});


// get all the tags available and set up autocomplete
$.getJSON('/api/get_tag_labels', {foo: 'bar'}, function(data, jqXHR){
    // do something with response
    tag_labels = data["suggestions"];
    $('#tag-selection-input').autocomplete({
      lookup: tag_labels,
      lookupLimit: 20,
      autoSelectFirst: true,
      minChars: 0,
      onSelect: function (suggestion) {
        var value = suggestion.value;
        var span = "<span class=\"closebtn\" onclick=\"this.parentElement.style.display='none'\">&times;</span>"
        var chip = $("<div class=\"chip\">"
            + value + span + "</div>").hide();
        chip.appendTo($("#tags-container")).fadeIn(200);
        $("#tag-selection-input").val("");
      }
    });
});




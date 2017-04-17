$( document ).ready(function() {

    $("#search-button").click(function(event){
      // $.ajax({
      //   url: "",
      //   type: "get", //send it through get method
      //   data: { 
      //     user_query: $("#user-selection-input").val(), 
      //     tags: get_query_tags()
      //   },
      //   success: function(response) {
      //     //Do Something
      //   },
      //   error: function(xhr) {
      //     //Do Something to handle error
      //   }
      // });
      data = { 
          user_query: $("#user-selection-input").val(), 
          tags: get_query_tags()
      }
      $.get('/pt/api/search', data, function(response){
        var results = response["results"];
        var formatted = "";
        for(i = 0; i < results.length; i++){
          formatted += (i+1) + " " + results[i] + "\n";
        }
        $("#result").html(formatted);
      });
    });
});

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

$.getJSON('/pt/api/get_users_handles', {foo: 'bar'}, function(data, jqXHR){
    // do something with response
    users = data["suggestions"];
    $('#user-selection-input').autocomplete({
      lookup: users,
      lookupLimit: 5,
      autoSelectFirst: true,
      onSelect: function (suggestion) {
          var twitter_handle = suggestion.split(" ")[0]
          $.getJSON('/pt/api/get_user_info', {twitter_handle: twitter_handle}, function(data, jqXHR){
              var user_data = data.user_data;
              var user_tags = data.user_tags;
              $("#user_name").text(user_data.name);
              $("#user_handle").attr("href","twitter.com/" + user_data.twitter_handle);
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

$.getJSON('/pt/api/get_tag_labels', {foo: 'bar'}, function(data, jqXHR){
    // do something with response
    tag_labels = data["suggestions"];
    $('#tag-selection-input').autocomplete({
      lookup: tag_labels,
      lookupLimit: 5,
      autoSelectFirst: true,
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



// $('#user-selection-input').autocomplete({
//     serviceUrl: '/pt/ajax/get_users_handles',
//     onSelect: function (suggestion) {
//         console.log(suggestion);
//     }
//     // transformResult: function(response) {
//     //   console.log(response);
//     //   console.log(JSON.parse(response));
//     //   return JSON.parse(response);
//     //   // return {"suggestion": ["hello", "world"]}
//     // }
// });


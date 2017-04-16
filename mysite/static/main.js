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
      $.get('/pt/ajax/search', data, function(response){
        
      });
    });
});

function get_query_tags(){
  tags = [];
  $('#tags-container').children().each(function () {
      if($(this).style == null){
        tag = $(this).html().split("<")[0];
        tags.push(tag);
      }
  });
  return tags;
}

$.getJSON('/pt/ajax/get_users_handles', {foo: 'bar'}, function(data, jqXHR){
    // do something with response
    users = data["suggestions"];
    $('#user-selection-input').autocomplete({
      lookup: users,
      lookupLimit: 5,
      autoSelectFirst: true,
      onSelect: function (suggestion) {
          
      }
    });
});

$.getJSON('/pt/ajax/get_tag_labels', {foo: 'bar'}, function(data, jqXHR){
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


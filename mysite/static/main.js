$( document ).ready(function() {

    $("#search-button").click(function(event){
      data = { 
          user_query: $("#user-selection-input").val(), 
          tags: get_query_tags()
      }
      $.get('/pt/ajax/search', data, function(response){
        var results = response["results"];

        $("#result").empty();
        var listGroup = $("<ol class=\"list-group\"></ol>");

        for(i = 0; i < results.length; i++){
          var listItem = $("<li class=\"list-group-item\"></li>");
          result = results[i]
          var formattedItem = listItem.html(result[0] + " " + (result[1] * 100).toFixed(2) + "%");
          listGroup.append(formattedItem);
        }
        if(results.length == 0){
          var empty = listItem.html("No results found");
          listGroup.append(empty);
        }
        $("#result").append(listGroup);
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


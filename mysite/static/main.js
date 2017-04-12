$( document ).ready(function() {
    console.log( "ready!" );

    // $("#tag-selection-input").on('keyup', function (e) {
    //     if (e.keyCode == 13) {
    //         // Do something
    //         span = "<span class=\"closebtn\" onclick=\"this.parentElement.style.display='none'\">&times;</span>"
    //         $("#tags-container").append("<div class=\"chip\">" 
    //           + $(this).val() + span + "</div>")
    //         e.stopPropagation();
    //     }
    // });

    $("#search-button").click(function(event){
      alert("pressed search");
    });
});

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
        value = suggestion.value;
        span = "<span class=\"closebtn\" onclick=\"this.parentElement.style.display='none'\">&times;</span>"
        $("#tags-container").append("<div class=\"chip\">"
            + value + span + "</div>");
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
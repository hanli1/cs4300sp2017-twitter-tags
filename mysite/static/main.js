$( document ).ready(function() {
    console.log( "ready!" );
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
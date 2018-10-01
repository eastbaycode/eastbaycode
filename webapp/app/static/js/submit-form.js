$(document).ready(function(){
    $('form').on('submit', function(event) {
        $.ajax({
            data : {
                code: editor.getSession().getValue()
            },
            type : 'POST',
            url : '/process'
        })
        .done(function(data){
            if (data.error){
                $('#errorAlert').text(data.error).show();
                $('#successAlert').hide();
            }
            else{
                $('#successAlert').text(data.code).show();
                $('#errorAlert').hide();
            }
        });
        event.preventDefault();
    });
});

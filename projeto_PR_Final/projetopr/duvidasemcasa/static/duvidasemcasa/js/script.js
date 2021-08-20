$(document).ready(function(event){
    $("#controla-nav").click(function(){
        $("nav").toggle();
    });

    $("#confirma").keyup(function(){
             if ($("#confirma").val() != $("#pass").val()) {
                 $("#msg").html(" Palavras-Passe não identicas!").css("color","red");
                 $("#registar").attr("disabled", true);
             }else{
                 $("#msg").html(" ").css("color","red");
                 $('#registar').attr("disabled", false);
            }
      });

    $("#pass").keyup(function(){
             if ($("#confirma").val() != $("#pass").val()) {
                 $("#msg").html(" Palavras-Passe não identicas!").css("color","red");
                 $("#registar").attr("disabled", true);
             }else{
                 $("#msg").html(" ").css("color","red");
                 $('#registar').attr("disabled", false);
            }
      });

    $(window).resize(function(){
        var win = $(this);
        if (win.width() > 768){
            $("nav").show();
        }
    })

    $('#myfile').change(function(){
        var files = $('#myfile')[0].files;
        if(files.length > 5){
            $("#msg").html(" Só pode enviar 5 ficheiros").css("color","red");
            $('#submeter').attr("disabled", true);
        }else{
            $("#msg").html(" ").css("color","red");
            $('#submeter').attr("disabled", false);
        }
    });

    $('.aviso').click(function () {
        $(this).remove()
    })
});

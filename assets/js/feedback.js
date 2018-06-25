  $(function($) {
    $('#feedback').on('click',function(e){
    e.preventDefault();
    e.stopPropagation();
    $('#feedbackForm textarea, #feedbackForm input:not([type="submit"])').val('');
    $('#feedbackForm').modal({show:true});
  });
  $('#feedbackForm [id]').on('focus', function(e) {
    if ($(e.currentTarget).parent().hasClass('has-error'))
      $(e.currentTarget).parent().removeClass('has-error').find('span').css('visibility', 'hidden');
  });
  $('#feedbackForm').on('shown.bs.modal', function() {
    $('#feedbackForm textarea').focus();
  });

  $('#feedbackForm input[type="submit"]').on('click', function (e) {
    var valid = true;
    $('#feedbackForm [id]').each(function (i, v) {
      if ($(v).val() === '') {
        $(v).parent().addClass('has-error').find('span').css('visibility', 'visible');
        valid = false;
      }
      else
        if ($(v).attr('id') === 'feedback-email' && !validateEmail($(v).val())) {
          $(v).parent().addClass('has-error').find('span').css('visibility', 'visible');
          valid = false;
        }
    });
    if (valid)
      $.ajax({
        url   : 'https://oceansMap2.asascience.com/?SiteID=1&Name=' + $('#feedback-name').val() + '&Email=' + $('#feedback-email').val() + '&Comment=' + $('#feedback-comment').val(),
        type  : 'POST',
        success: function (data) {
          alert('Feedback Submitted');
          $('#feedbackForm').modal('hide');
        },
        error: function (error) {
          alert('An Error has Occurred');
        }
      });

    $(e.currentTarget).blur();
  });
  function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
  }
});
function show_samples(div_id) {
    $(div_id).jqm({ajax: '/sample_popup', trigger: 'div.dialog',
                  ajaxText: 'Please wait while we load that for you'});}
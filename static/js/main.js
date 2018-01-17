$(document).ready(function () {
    vex.defaultOptions.className = 'vex-theme-default';
    vex.dialog.buttons.YES.text = 'Sim';
    vex.dialog.buttons.NO.text = 'Não';
    jQuery.datetimepicker.setLocale('pt');

    $(document).on('click', '#login_button', userLogin);

    $(document).on('click', '#nav_menu > li.nav_item', function(){
        window.location.href = $(this).attr('data-link');
    });

    $(document).on('click', 'button.table_toggle', toggleTables);

    $(document).on('change', '.row:not(.header) input[type="checkbox"]', regularCheckBoxChanged);

    $(document).on('change', '.row.header input[type="checkbox"]', generalCheckBoxChanged);

    $(document).on('click', '.material-icons.general_option.users', generalUserOptionClicked);

    $(document).on('click', '.material-icons.general_option.partners', generalPartnerOptionClicked);

    $(document).on('click', '.material-icons.general_option.reports', generalReportOptionClicked);

    $(document).on('click', '.material-icons.general_option.spots', generalSpotOptionClicked);

    $(document).on('click', '.material-icons.user_option', userOptionClicked);

    $(document).on('click', '.material-icons.report_option', reportOptionClicked);

    $(document).on('click', '.material-icons.partner_option', partnerOptionClicked);

    $(document).on('click', '.material-icons.spot_option', spotOptionClicked);

    $(document).on('click', '#add_new_partner', addNewPartner);

    $(document).on('click', '#add_new_spot', addNewSpot);

    $(document).on('change', '#new_partner_file_input', changedNewPartnerPicInDialog);

    $(document).on('change', 'input[type="radio"][name="image_type_chooser"]', imageTypeChooser);

    $(document).on('change keyup', '#new_partner_img_url', imageFromUrlChanged);

    $(document).on('click', '.spot_info_option', spotInfoOptionClicked);

    $(document).on('click', '.spot_image_option', spotImageOptionClicked);

    $(document).on('click', '.spot_images > .spot_image', clickSpotImage);

    $(document).on('change', '.spot_image_file_input', spotImageFileInputChanged);

    $(document).on('change', '#main_report_types', mainReportTypeSelectChanged);

    $(document).on('change', '#secondary_report_types', secondaryReportTypeSelectChanged);

    $(document).on('keyup change', 'input[type="number"].coords', coordsChangedOnNewSpot);

    $(document).on('change', '.form_spot_type > input[type="checkbox"]', newSpotFormCboxChanged);

    $(document).on('click', '#add_new_shop_item', addNewShopItem);

    $(document).on('click', '#add_new_event', addNewEvent);

    function renderNewEventForm(missions, shop_items){
        let form = '';
        form += '<label for="name">Nome</label>';
        form += '<input type="text" name="name" required>';
        form += '<label for="desc">Descrição</label>';
        form += '<textarea name="desc" required></textarea>';
        form += '<span style="display: block; margin-top: 1vh;">Período</span>';
        form += '<div class="row">';
        form += '<div class="col s6 ha-left va-mid" style="padding-right: 1vw;">';
        form += '<label for="starts_at">Início</label>';
        form += '<input type="text" name="starts_at" class="datetimepicker" required>';
        form += '</div>';
        form += '<div class="col s6 ha-left va-mid">';
        form += '<label for="ends_at">Fim</label>';
        form += '<input type="text" name="ends_at" class="datetimepicker" required>';
        form += '</div></div>';
        form += '<span style="display: block; margin-top: 1vh;">Localização</span>';
        form += '<div class="row"><div class="col s12 ha-mid va-mid" id="new_event_map"></div></div>';
        form += '<label for="coords">Coordenadas</label>';
        form += '<input type="text" name="coords" id="new_event_local" required>';
        form += '<span style="display: block; margin-top: 1vh;">Recompensas</span>';
        form += '<div class="row">';
        form += '<div class="col s2 ha-left va-mid" style="padding-right: 1vw;">';
        form += '<label for="fire_essences">Essências de Fogo</label>';
        form += '<input type="number" step="1" min="0" name="fire_essences" value="0" required>';
        form += '</div>';
        form += '<div class="col s2 ha-left va-mid" style="padding-right: 1vw;">';
        form += '<label for="water_essences">Essências de Água</label>';
        form += '<input type="number" step="1" min="0" name="water_essences" value="0" required>';
        form += '</div>';
        form += '<div class="col s2 ha-left va-mid" style="padding-right: 1vw;">';
        form += '<label for="wind_essences">Essências de Vento</label>';
        form += '<input type="number" step="1" min="0" name="wind_essences" value="0" required>';
        form += '</div>';
        form += '<div class="col s2 ha-left va-mid" style="padding-right: 1vw;">';
        form += '<label for="spirit_essences">Essências de Espírito</label>';
        form += '<input type="number" step="1" min="0" name="spirit_essences" value="0" required>';
        form += '</div>';
        form += '<div class="col s2 ha-left va-mid" style="padding-right: 1vw;">';
        form += '<label for="earth_essences">Essências de Terra</label>';
        form += '<input type="number" step="1" min="0" name="earth_essences" value="0" required>';
        form += '</div>';
        form += '<div class="col s2 ha-left va-mid">';
        form += '<label for="points">Pontos</label>';
        form += '<input type="number" step="1" min="0" name="points" value="0" required>';
        form += '</div>';
        form += '</div>';
        form += '<span style="display: block; margin-top: 1vh;">Escolher missões</span>';
        form += '<div style="display:block; width: 100%;">';
        $.each(missions, function(i, mission){
            form += '<div style="display:inline-block; width: 50%;">';
            form += '<div class="row" style="padding: 1vh 1vw; margin-bottom: 10px; background-color: rgba(52, 152, 219, 0.2);">';
            form += '<div class="col s10 ha-left va-mid">';
            form += '<span style="display:block; margin-bottom: 5px; font-size: 0.9em;">'+mission.name['pt']+'</span>';
            form += '<span style="display:block; font-size: 0.8em; opacity: 0.6;">'+mission.description['pt']+'</span>';
            form += '</div>';
            form += '<div class="col s2 ha-mid va-mid noselect">';
            form += '<label for="mission_'+mission.id+'"><i class="material-icons">check_box_outline_blank</i></label>';
            form += '<input style="display:none;" type="checkbox" name="missions" value="'+mission.id+'" id="mission_'+mission.id+'" required>';
            form += '</div></div></div>';
        });
        if(missions.length === 0)
            form += '<div class="row"><div class="col s12 ha-left va-mid">Não há missões para escolher</div></div>';
        form += '</div>';

        form += '';
        form += '';
        form += '';
        form += '';
        form += '';
        form += '';
        return form;
    }

    function addNewEvent() {
        $.get('/get_new_event_info', function(res){
            if(res.code === 1){
                console.log(res);
                vex.dialog.open({
                message: 'Agendar novo evento',
                input: renderNewEventForm(res.missions, res.shop_items),
                buttons: [
                    $.extend({}, vex.dialog.buttons.YES, {text: 'Agendar'}),
                    $.extend({}, vex.dialog.buttons.NO, {text: 'Cancelar'})
                ],
                afterOpen: function(){
                    $('.vex-content').css('width', '70%');
                    $(this).css('width', '60%');
                    $('.datetimepicker').datetimepicker({
                        i18n:{
                            pt: {
                                months:[
                                    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro",
                                    "Outubro", "Novembro", "Dezembro"
                                ],
                                dayOfWeek:[
                                    "Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"
                                ]
                            }
                        }
                    });

                    $('#new_event_map').css('height', '40vh');

                    let new_event_map = new google.maps.Map(document.getElementById('new_event_map'), {
                        center: {lat: 41.444266, lng: -8.292241},
                        zoom: 16,
                        fullscreenControl: true,
                        streetViewControl: false
                    });

                    let event_marker = null;
                    google.maps.event.addListener(new_event_map, 'click', function(event){
                        let pos = event.latLng;
                        let local = pos.lat() + ", " + pos.lng();
                        console.log(local);
                        if(event_marker == null){
                            event_marker = new google.maps.Marker({
                                position: new google.maps.LatLng(pos.lat(), pos.lng()),
                                map: new_event_map
                            });
                        } else {
                            event_marker.setMap(new_event_map);
                            event_marker.setPosition(new google.maps.LatLng(pos.lat(), pos.lng()));
                        }

                        $('#new_event_local').val(local);
                    });
                },
                callback: function(data){
                    if(data) {
                        console.log(data);
                    }
                }
            });
            }
        });
    }
    
    function renderNewShopItemForm(partners){
        let form = '<label for="name">Nome</label>';
        form += '<input name="name" type="text" required autocomplete="off">';
        form += '<label for="cost">Preço (em pontos)</label>';
        form += '<input name="cost" type="number" min="25" step="10" value="25" required autocomplete="off">';
        form += '<label for="partner">Entidade que o disponibiliza</label>';
        form += '<select name="partner">';
        form += '<option value="-1">Sem parceria</option>';
        $.each(partners, function(i, p){
            form += '<option value="'+p.id+'">'+p.name+'</option>';
        });
        form += '</select>';
        form += '';
        form += '';
        form += '';
        form += '';
        form += '';
        form += '';
        return form;
    }

    function addNewShopItem(){
        $.get('/get_partner_list', function(res){
            if(res.code === 1){
                vex.dialog.open({
                message: 'Adicionar produto à loja',
                input: renderNewShopItemForm(res.partners),
                buttons: [
                    $.extend({}, vex.dialog.buttons.YES, {text: 'Adicionar'}),
                    $.extend({}, vex.dialog.buttons.NO, {text: 'Cancelar'})
                ],
                callback: function(data){
                    if(data) {
                        console.log(data);
                        /*
                        $.ajax({
                            url: '/save_new_spot',
                            type: 'POST',
                            data: JSON.stringify(data),
                            processData: false,
                            contentType: "application/json; charset=utf-8",
                            dataType: "json",
                            success: function (res) {
                                console.log(res);
                                if(res.code === 1){
                                    window.location.reload(true);
                                }
                            }
                        });
                         */
                    }
                }
            });
            }
        });
    }

    function mainReportTypeSelectChanged(){
        let value = parseInt($(this).val());
        let sec = $('#secondary_report_types');
        if(value === -1){
            sec.css('visibility', 'hidden');
            $('.row.report').show();
        } else {
            sec.css('visibility', 'visible');
            sec.find('option').hide();
            sec.find('option').first().show();
            sec.find('option[data-parent="'+value+'"]').show();
            sec.val(sec.find('option').first().attr('value'));
            sec.change();
        }
    }

    function secondaryReportTypeSelectChanged(){
        let value = parseInt($(this).val());
        $('.row.report').hide();
        if(value === -1){
            $('.row.report[data-prtype="'+$('#main_report_types').val()+'"]').show();
        }
        else {
            $('.row.report[data-rtype="'+value+'"]').show();
        }
    }

    function sendReportActionToServer(info){
        $.ajax({
            url: '/admin_report_action',
            type: 'POST',
            data: JSON.stringify(info),
            processData: false,
            contentType: "application/json; charset=utf-8",
            dataType : "json",
            success: function(res){
                if(res.code === 1){
                    let table;
                    $.each(info['ids'], function(i, id){
                        if(i===0)
                            table = $('.row.report[report-id="'+id+'"]').parent();
                        if(res.action === 'delete') {
                            $('.row.report[report-id="' + id + '"]').remove();
                            $('.report_info[for="' + id + '"]').remove();
                        }
                        else {
                            let row = $($('.row.report[report-id="'+id+'"]').detach());
                            let report_info = $($('.report_info[for="'+id+'"]').detach());
                            let icons = row.find('.col').last();
                            if(res.action === 'analize'){
                                row.appendTo('#active_reports');
                                let options = '<i class="material-icons report_option" data-action="info" title="Ver detalhes">info</i><i class="material-icons report_option" data-action="delete" title="Apagar participação">delete</i>';
                                options += '<i class="material-icons report_option" data-action="done" title="Passar para \'Resolvidas\'">done</i>';
                                options += '<i class="material-icons report_option" data-action="special" title="Passar para \'Casos Especiais\'">folder_special</i>';
                                icons.html(options);
                            }
                            else if(res.action === 'done'){
                                row.appendTo('#solved_reports');
                                icons.html('<i class="material-icons report_option" data-action="info" title="Ver detalhes">info</i>');
                            }
                            else if(res.action === 'special'){
                                row.appendTo('#special_cases_reports');
                                icons.html('<i class="material-icons report_option" data-action="info" title="Ver detalhes">info</i><i class="material-icons report_option" data-action="done" title="Passar para \'Resolvidas\'">done</i>');
                            }
                            report_info.hide();
                            row.after(report_info);
                            row.find('input[type="checkbox"]').prop('checked', false).change();
                        }
                    });
                    table.find('input[type="checkbox"]:checked').prop('checked', false).change();
                    table.find('.general_option').removeClass('active');
                    /*
                    table.find('input[type="checkbox"]:checked').prop('checked', false).change();
                    table.find('label').each(function(){
                        $(this).find('.material-icons').text('check_box_outline_blank');
                    });
                    table.find('.general_option').removeClass('active');
                    */
                    if(info['ids'].length > 1)
                        vex.dialog.alert({message: 'Estado das participações selecionadas alterado com sucesso'});
                    else if(info['ids'].length === 1)
                        vex.dialog.alert({message: 'Estado da participação selecionada alterado com sucesso'});
                }
                else if(res.code === -1){
                    vex.dialog.alert({
                        message: 'Ocorreu um erro ao tentar realizar a operação, por favor tente mais tarde.'
                    });
                }
                else {
                    vex.dialog.alert({
                        message: 'Acção inválida ou não tem autorização para realizar esta operação'
                    });
                }
            }
        });
    }

    function generalReportOptionClicked(){
        let my_table = $(this).parent().parent().parent();
        let my_action = $(this).attr('data-action');
        let ids = [];
        my_table.find('.row:not(.title):not(.header)').each(function(){
            if($(this).find('input[type="checkbox"]').is(':checked')){
                ids[ids.length] = parseInt($(this).attr('report-id'));
            }
        });
        let info = {
            'ids': ids,
            'action': my_action
        };
        let message;
        switch (my_action){
            case 'delete':
                message = 'Quer mesmo APAGAR as participações selecionadas?';
                break;
            case 'analize':
                message = 'Passar participações selecionadas para análise?';
                break;
            case 'done':
                message = 'Dar participações selecionadas como resolvidas?';
                break;
            case 'special':
                message = 'Tratar as participações selecionadas como casos especiais?';
                break;
            default:
                console.log("general report action not treated");
        }
        vex.dialog.confirm({
            'message': message,
            callback: function(choice){
                if(choice){
                    sendReportActionToServer(info);
                }
                return false;
            }
        });
    }

    function reportOptionClicked(){
        let id = parseInt($(this).parent().parent().attr('report-id'));
        let action = $(this).attr('data-action');
        let info = {
            'ids': [id],
            'action': action
        };

        if(action === 'info'){
            let este = $('.report_info[for="'+id+'"]');
            if(este.is(':visible')){
                este.hide();
                return false;
            }
            $('.report_info').hide();
            este.show();
            return false;
        }
        if(action === 'delete'){
            vex.dialog.confirm({
                'message': 'APAGAR ' + spot_name + '?',
                callback: function(choice){
                    if(choice){
                        sendReportActionToServer(info);
                    }
                    return false;
                }
            });
        } else if(action === 'special' || action === 'done' || action === 'analize'){
            sendReportActionToServer(info);
        }
    }

    function spotImageFileInputChanged(){
        let spot_id = parseInt($(this).parent().attr('spot-id'));
        console.log("changed input from spot id: "+spot_id);

        let files = $('#image_input_'+spot_id+'')[0].files;
        if(files.length === 0)
            return false;
        let count = 0;
        $.each(files, function(i, file){
            if(typeof file !== 'undefined' && file.type.match(/image.*/)) {
                count++;
            }
        });

        vex.dialog.confirm({
            message: 'Carregar '+count+' imagens?',
            callback: function(choice){
                if(choice){
                    let formdata = new FormData();
                    formdata.append('action', 'add');
                    $.each(files, function(i, file){
                        if(typeof file !== 'undefined' && file.type.match(/image.*/)) {
                            if(window.FileReader){
                                let reader = new FileReader();
                                reader.readAsDataURL(file);
                                formdata.append('pic', file);
                            }
                        }
                    });
                    sendSpotImageAction(spot_id, formdata);
                }
            }
        });
    }

    function clickSpotImage(){
        $(this).toggleClass('chosen');
        let buttons = $('.spot_info[for="'+$(this).parent().attr('data-spot-id')+'"]').find('.spot_image_option.select');


        if($(this).parent().find('.spot_image.chosen').length > 0){
            buttons.show();
        }
        else {
            buttons.hide();
        }
        return false;
    }

    function sendSpotImageAction(spot_id, formdata){
        $.ajax({
            url: '/admin_spot_image_action/'+spot_id,
            type: 'POST',
            data: formdata,
            processData: false,
            contentType: false,
            xhrFields: {withCredentials: true},
            success: function(res){
                if(res.code === 1){
                    if(res.action === 'add'){
                        let string = "";
                        $.each(res.images, function(i, img_src){
                            string += '<div class="spot_image" data-src="'+img_src+'" style="background-image: url(\'static/spot_imgs/'+spot_id+'/'+img_src+'\');"><div class="hover"></div></div>';
                        });
                        $('.spot_images[data-spot-id="'+spot_id+'"]').html(string);
                    }
                    else if(res.action === 'delete'){
                        $.each(res.removed, function(i, img_src){
                             $('.spot_images[data-spot-id="'+spot_id+'"]').find('.spot_image[data-src="'+img_src+'"]').remove();
                        });
                        let spot_info = $('.spot_info[for="'+spot_id+'"]');
                        spot_info.find('.spot_image').removeClass('chosen');
                        spot_info.find('.spot_image_option.select').hide();
                        vex.dialog.alert({message: res.removed.length + ' imagens apagadas'});
                    }
                    return false;
                } else if(res.code === 0) {
                    vex.dialog.alert({message:'Ocorreu um erro ao editar informação de parceiro, por favor tente mais tarde'});
                } else {
                    vex.dialog.alert({message:'Não tem autorização para realizar esta acção'});
                }
            }
        });
    }

    function spotImageOptionClicked(){
        let spot_id = parseInt($(this).parent().attr('spot-id'));
        let spot_info = $('.spot_info[for="'+spot_id+'"]');

        switch ($(this).attr('data-action')) {
            case "clear":
                spot_info.find('.spot_image').removeClass('chosen');
                spot_info.find('.spot_image_option.select').hide();
                return false;
                break;
            case "delete":
                let formdata = new FormData();
                formdata.append('action', 'delete');
                let list = [];
                spot_info.find('.spot_image.chosen').each(function(){
                    list.push($(this).attr('data-src'));
                });
                formdata.append('list', JSON.stringify(list));
                sendSpotImageAction(spot_id, formdata);
                break;
            case "add":
                $('#image_input_'+spot_id+'').click();
                break;
            default:
                console.log("Untreated spot image option clicked");
        }
    }

    function spotInfoOptionClicked(){
        let spot_id = parseInt($(this).parent().attr('spot-id'));
        let spot_info = $('.spot_info[for="'+spot_id+'"]');
        let action = $(this).attr('data-action');

        if(action === 'edit'){
            $(this).parent().find('.spot_info_option').show();
            $(this).hide();
            spot_info.find('.spot_types').show();
            spot_info.find('textarea, input').removeAttr('readonly');
        }
        else if(action === 'cancel'){
            let este = $(this);
            vex.dialog.confirm({
                message: 'Descartar alterações feitas à informação do local?',
                callback: function(choice){
                    if(choice){
                        let name = $('#name_input_spot_'+spot_id+'');
                        let desc = spot_info.find('textarea');
                        let loct = $('#location_input_spot_'+spot_id+'');

                        name.val(typeof name.attr('data-original') === 'undefined' || name.attr('data-original').length === 0 ? "" : name.attr('data-original'));
                        desc.val(typeof desc.attr('data-original') === 'undefined' || desc.attr('data-original').length === 0 ? "" : desc.attr('data-original'));
                        loct.val(typeof loct.attr('data-original') === 'undefined' || loct.attr('data-original').length === 0 ? "" : loct.attr('data-original'));

                        este.parent().find('.spot_info_option').hide();
                        este.parent().find('.spot_info_option[data-action="edit"]').show();
                        spot_info.find('textarea, input').attr('readonly', 'readonly');

                        spot_info.find('.spot_type').each(function(){
                            $(this).find('input[type="checkbox"]').prop('checked', ($(this).attr('data-original-checked-value') === 'yes')).change();
                        });
                        spot_info.find('.spot_types').hide();
                    }
                }
            });
        }
        else if(action === 'save'){
            let este = $(this);
            console.log("pedi para guardar");
            let name = $('#name_input_spot_'+spot_id+'');
            let desc = spot_info.find('textarea');
            let loct = $('#location_input_spot_'+spot_id+'');
            let type_ids = [];
            spot_info.find('.spot_type_check').each(function(){
                if($(this).is(':checked'))
                    type_ids.push(parseInt($(this).val()));
            });

            let info = {
                name: name.val(),
                description: desc.val(),
                location: loct.val(),
                ids: type_ids,
                spot_id: spot_id,
                action: action
            };

            $.ajax({
                url: '/admin_spot_action',
                type: 'POST',
                data: JSON.stringify(info),
                processData: false,
                contentType: "application/json; charset=utf-8",
                dataType : "json",
                success: function(res){
                    if(res.code === 1 && res.action === 'save'){
                        console.log("chegou bem");
                        este.parent().find('.spot_info_option').hide();
                        este.parent().find('.spot_info_option[data-action="edit"]').show();
                        let valores = info['location'].split(", ");
                        let latf = parseFloat(valores[0]).toFixed(6), lngf = parseFloat(valores[1]).toFixed(6);
                        loct.val(latf+", "+lngf);

                        let spot_row = $('.row.spot[spot-id="'+spot_id+'"]');
                        spot_row.find('.col').eq(1).text(name.val());
                        spot_row.find('.col').eq(2).find('a').attr('href', 'https://www.google.com/maps/@'+latf+","+lngf+",20z");
                        spot_row.find('.col').eq(2).find('a').attr('title', loct.val());
                        spot_info.find('textarea, input').attr('readonly', 'readonly');

                        let type_string = "";
                        spot_info.find('.spot_type').each(function(){
                            let check = $(this).find('input[type="checkbox"]');
                            if(check.is(':checked')){
                                let label_text = $('label[for="'+check.attr('id')+'"]').text().replace('check_box ', '');
                                type_string += label_text + ", ";
                            }
                            $(this).attr('data-original-checked-value', check.is(':checked') ? 'yes' : 'no');
                        });
                        spot_row.find('.col').eq(3).text(type_string.slice(0, -2));
                        spot_info.find('.spot_types').hide();
                    }
                    else if(res.code === -1){
                        vex.dialog.alert({
                            message: 'Ocorreu um erro ao alterar informação do local, por favor tente mais tarde.'
                        });
                    }
                    else {
                        vex.dialog.alert({
                            message: 'Acção é inválida ou não tem autorização para a realizar'
                        });
                    }
                }
            });
        }
        return false;
    }

    function imageFromUrlChanged(){
        let imtype = $('input[type="radio"][name="image_type_chooser"]:checked').val();
        if(imtype === 'url'){
            let urlfield = $('#new_partner_img_url');
            if((urlfield.val()).replace(" ", "").length > 0 && isValidURL(urlfield.val())){
                let img = $('#new_partner_picture');
                img.attr('src', urlfield.val());

                setTimeout(function(){
                    if(img.width() * img.height() === 0){
                        img.attr('src', img.attr('data-original-src'));
                        urlfield.val("");
                        alert("Link não contem imagem, por favor escolher outro");
                    }
                }, 300);

            } else {
                $('#new_partner_picture').attr('src', $('#new_partner_picture').attr('data-original-src'));
            }
        }
    }

    function isValidURL(str) {
        if(typeof str === 'undefined')
            return false;
        let url = str;
        if (url.substring(0,7) !== 'http://' && url.substring(0,8) !== 'https://') {
            url = 'http://' + str;
        }
        let a  = document.createElement('a');
        a.href = url;
        return (a.host && a.host !== window.location.host);
    }

    function renderEditPartnerForm(partner){
        console.log(partner);
        let form = '<label for="name">Nome (obrigatório)</label>';
        form += '<input name="name" type="text" required autocomplete="off" value="'+partner.name+'">';
        form += '<label for="link">Link do site</label>';
        form += '<input name="link" type="text" autocomplete="off" value="'+(partner.url == null ? "" : partner.url)+'">';
        form += '<label for="desc">Descrição</label>';
        form += '<textarea name="desc" autocomplete="off">'+(partner.description != null && typeof partner.description.pt !== 'undefined' ? partner.description.pt : "")+'</textarea>';
        form += '<div class="row"><div class="col s12 ha-left va-mid">Imagem</div></div>';
        form += '<div class="row" id="new_partner_radios"><div class="col s6 ha-mid va-mid">';

        if(partner.logo.type === 'url' || partner.logo.type === 'none'){
            form += '<input type="radio" name="image_type_chooser" value="url" id="type_url_image" checked>';
            form += '<label for="type_url_image">URL</label></div><div class="col s6 ha-mid va-mid">';
            form += '<input type="radio" name="image_type_chooser" value="static" id="type_static_image">';
            form += '<label for="type_static_image">Ficheiro Local</label></div></div>';
            form += '<div id="hosted_image_div">';
            form += '<label for="img_url">URL da imagem</label>';
            form += '<input name="img_url" id="new_partner_img_url" type="text" autocomplete="off" value="'+partner.logo.src+'"></div>';
            form += '<div id="local_image_div" style="display: none;"><div class="row"><div class="col s12 ha-left va-mid">';
            form += '<input name="logo" id="new_partner_file_input" type="file" accept="image/*"></div></div></div>';
        }
        else {
            form += '<input type="radio" name="image_type_chooser" value="url" id="type_url_image">';
            form += '<label for="type_url_image">URL</label></div><div class="col s6 ha-mid va-mid">';
            form += '<input type="radio" name="image_type_chooser" value="static" id="type_static_image" checked>';
            form += '<label for="type_static_image">Ficheiro Local</label></div></div>';
            form += '<div id="hosted_image_div" style="display: none;">';
            form += '<label for="img_url">URL da imagem</label>';
            form += '<input name="img_url" id="new_partner_img_url" type="text" autocomplete="off" value=""></div>';
            form += '<div id="local_image_div"><div class="row"><div class="col s12 ha-left va-mid">';
            form += '<input name="logo" id="new_partner_file_input" type="file" accept="image/*"></div></div></div>';
        }

        form += '<div class="row"><div class="col s12 ha-mid va-mid">';
        if(partner.logo.type === 'none')
            form += '<img id="new_partner_picture" data-original-src="/static/partner_logos/no_pic.jpg" src="/static/partner_logos/no_pic.jpg">';
        else if(partner.logo.type === 'url')
            form += '<img id="new_partner_picture" data-original-src="'+partner.logo.src+'" src="'+partner.logo.src+'">';
        else
            form += '<img id="new_partner_picture" data-original-src="/static/partner_logos/'+partner.logo.src+'" src="/static/partner_logos/'+partner.logo.src+'">';

        form += '</div></div>';
        form += '<div class="row"><div class="col s12 ha-left va-mid">Localização</div></div><div class="row">';
        form += '<div class="col s6 va-mid ha-left"><label for="lat">Latitude</label>';
        form += '<input name="lat" type="text" autocomplete="off" placeholder="Exemplo: 41.447877" value="'+(partner.gps_location.lat == null ? "" : partner.gps_location.lat)+'">';
        form += '</div><div class="col s6 va-mid ha-left"><label for="lng">Longitude</label>';
        form += '<input name="lng" type="text" autocomplete="off" placeholder="Exemplo: -8.290308" value="'+(partner.gps_location.lng == null ? "" : partner.gps_location.lng)+'">';
        form += '</div></div><div class="row"><div class="col s12 ha-left va-mid"><label for="address">Morada</label>';
        form += '<textarea name="address" autocomplete="off">'+(partner.address == null ? "" : partner.address)+'</textarea>';
        form += '</div></div>';
        return form;
    }

    function editPartnerInfo(partner_id){
        $.get('/get_partner_info/'+partner_id, function(res){
            //console.log(res);
            vex.dialog.open({
                message: 'Criar Novo Parceiro',
                input: renderEditPartnerForm(res.partner),
                buttons: [
                    $.extend({}, vex.dialog.buttons.YES, {text: 'Modificar'}),
                    $.extend({}, vex.dialog.buttons.NO, {text: 'Cancelar'})
                ],
                callback: function (data) {
                    if(data){
                        console.log(data);
                        if (data.name.length > 0) {
                            let formdata = new FormData();
                            formdata.append('name', data.name);
                            if(typeof data.desc === 'undefined' || (typeof data.desc !== 'undefined' && data.desc.length === 0))
                                formdata.append('desc', null);
                            else
                                formdata.append('desc', data.desc);
                            let lat_reg = new RegExp("^(\\+|-)?(?:90(?:(?:\\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\\.[0-9]{1,6})?))$");
                            let lng_reg = new RegExp("^(\\+|-)?(?:180(?:(?:\\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\\.[0-9]{1,6})?))$");
                            let lat = null, lng = null;

                            if(typeof data.lat !== 'undefined' && lat_reg.exec(data.lat)){
                                lat = data.lat;
                            }
                            if(typeof data.lng !== 'undefined' && lng_reg.exec(data.lng)){
                                lng = data.lng;
                            }
                            formdata.append('gps', JSON.stringify({'lat': lat, 'lng': lng}));

                            if(typeof data.address === 'undefined' || (typeof data.address !== 'undefined' && data.address.length === 0))
                                formdata.append('address', null);
                            else
                                formdata.append('address', data.address);

                            if(typeof data.link === 'undefined' || (typeof data.link !== 'undefined' && data.link.length === 0))
                                formdata.append('url', null);
                            else
                                formdata.append('url', data.link);

                            let imtype = $('input[type="radio"][name="image_type_chooser"]:checked').val();

                            if(imtype === 'url'){
                                let url = ($('#new_partner_img_url').val()).replace(" ", "");
                                if(url.length > 0) {
                                    formdata.append('src', url);
                                }
                                else if(res.partner.logo_img.type !== 'url'){
                                    imtype = res.partner.logo_img.type;
                                    if(res.partner.logo_img.type === 'none'){
                                        formdata.append('src', '');
                                    } else {
                                        formdata.append('src', $('#new_partner_picture').attr('data-original-src'));
                                    }
                                }
                            }
                            else { // TYPE: STATIC
                                let file = $('#new_partner_file_input')[0].files[0];
                                if(typeof file !== 'undefined' && file.type.match(/image.*/)){
                                    if(window.FileReader){
                                        let reader = new FileReader();
                                        reader.readAsDataURL(file);
                                        formdata.append('pic', file);
                                        formdata.append('src', 'filechange');
                                    }
                                }
                                else {
                                    if(res.partner.logo_img.type !== 'static'){
                                        imtype = res.partner.logo_img.type;
                                        if(res.partner.logo_img.type === 'none'){
                                            formdata.append('src', '');
                                        } else {
                                            formdata.append('src', $('#new_partner_picture').attr('data-original-src'));
                                        }
                                    }
                                }
                            }

                            formdata.append('imgtype', imtype);

                            $.ajax({
                                url: '/edit_partner_info/'+partner_id,
                                type: 'POST',
                                data: formdata,
                                processData: false,
                                contentType: false,
                                xhrFields: {withCredentials: true},
                                success: function(res){
                                    if(res.code === 1){
                                        let row = $('.row.partner[partner-id="'+partner_id+'"]');
                                        row.find('.col').eq(1).text(data.name);
                                        if(data.link !== 'undefined' && isValidURL(data.link)){
                                            row.find('.col').eq(2).html('<a href="'+data.link+'">'+data.link+'</a>');
                                        } else {
                                            row.find('.col').eq(2).text("-");
                                        }
                                    } else if(res.code === 0) {
                                        vex.dialog.alert({message:'Ocorreu um erro ao editar informação de parceiro, por favor tente mais tarde'});
                                    } else {
                                        vex.dialog.alert({message:'Não tem autorização para realizar esta acção'});
                                    }
                                }
                            });
                        }
                    }
                }
            });
        });
    }

    function changedNewPartnerPicInDialog(){
        let frame = $('#new_partner_picture');
        let file = $(this)[0].files[0];

        if(typeof file !== 'undefined' && file.type.match(/image.*/)){
            if(window.FileReader){
                let reader = new FileReader();
                reader.onloadend = function(){
                    frame.attr('src', reader.result);
                };
                reader.readAsDataURL(file);
            }
        }
        else {
            frame.attr('src', frame.attr('data-original-src'));
        }
    }

    function imageTypeChooser(){
        if($(this).val() === 'static'){
            $('#hosted_image_div').hide();
            $('#local_image_div').show();
        } else {
            $('#local_image_div').hide();
            $('#hosted_image_div').show();
        }
    }

    function coordsChangedOnNewSpot(){
        let changed = $(this);
        if(changed.attr('name') === 'lat'){

        }
        else if(changed.attr('name') === 'lng'){

        }
        changed.val(parseFloat(changed.val()).toFixed(6));
    }

    function newSpotFormCboxChanged(){
        let changed = $(this);
        $('label[for="'+changed.attr('id')+'"]').find('.material-icons').text(changed.is(':checked') ? 'check_box' : 'check_box_outline_blank');
    }

    function renderNewSpotForm(spot_types){
        let spot_form = '';
        spot_form += '<label for="name">Nome</label>';
        spot_form += '<input name="name" type="text" required autocomplete="off">';
        spot_form += '<label for="">Localização</label>';
        spot_form += '<div class="row">';
        spot_form += '<div class="col s6 va-top ha-left">';
        spot_form += '<label for="lat">Latitude</label>';
        spot_form += '<input name="lat" type="number" class="coords" required autocomplete="off" value="41.440913" step="0.000001">';
        spot_form += '</div>';
        spot_form += '<div class="col s6 va-top ha-left">';
        spot_form += '<label for="lng">Longitude</label>';
        spot_form += '<input name="lng" type="number" class="coords" required autocomplete="off" value="-8.289674" step="0.000001">';
        spot_form += '</div>';
        spot_form += '</div>';
        spot_form += '<label for="">Categoria(s)</label>';
        spot_form += '<div id="form_spot_types">';
        $.each(spot_types, function(i, st){
            spot_form += '<div class="form_spot_type">';
            spot_form += '<input type="checkbox" name="types" id="form_st_checkbox_'+st.id+'" value="'+st.name['en']+'" style="display:none;">';
            spot_form += '<label for="form_st_checkbox_'+st.id+'">';
            spot_form += '<i class="material-icons">check_box_outline_blank</i><span>'+st.name['pt_PT']+'</span>';
            spot_form += '</label></div>';
        });
        spot_form += '</div><label for="desc">Descrição do Local</label>';
        spot_form += '<textarea name="desc" required autocomplete="off"></textarea>';
        return spot_form;
    }

    function renderNewPartnerForm(){
        return [
            '<label for="name">Nome (obrigatório)</label>',
            '<input name="name" type="text" required autocomplete="off">',
            '<label for="link">Link do site</label>',
            '<input name="link" type="text" autocomplete="off">',
            '<label for="desc">Descrição</label>',
            '<textarea name="desc" autocomplete="off"></textarea>',
            '<div class="row"><div class="col s12 ha-left va-mid">Imagem</div></div>',

            '<div class="row" id="new_partner_radios"><div class="col s6 ha-mid va-mid">',
            '<input type="radio" name="image_type_chooser" value="url" id="type_url_image" checked>',
            '<label for="type_url_image">URL</label></div><div class="col s6 ha-mid va-mid">',
            '<input type="radio" name="image_type_chooser" value="static" id="type_static_image">',
            '<label for="type_static_image">Ficheiro Local</label></div></div>',
            '<div id="hosted_image_div">',
            '<label for="img_url">URL da imagem</label>',
            '<input name="img_url" id="new_partner_img_url" type="text" autocomplete="off">',
            '</div>',
            '<div id="local_image_div" style="display: none;">',
            '<div class="row"><div class="col s12 ha-left va-mid">',
            '<input name="logo" id="new_partner_file_input" type="file" accept="image/*">',
            '</div></div></div>',
            '<div class="row"><div class="col s12 ha-mid va-mid">',
            '<img id="new_partner_picture" data-original-src="/static/partner_logos/no_pic.jpg" src="/static/partner_logos/no_pic.jpg">',
            '</div></div>',
            '<div class="row"><div class="col s12 ha-left va-mid">Localização</div></div>',
            '<div class="row">',
            '<div class="col s6 va-mid ha-left">',
            '<label for="lat">Latitude</label>',
            '<input name="lat" type="text" autocomplete="off" placeholder="Exemplo: 41.447877">',
            '</div>',
            '<div class="col s6 va-mid ha-left">',
            '<label for="lng">Longitude</label>',
            '<input name="lng" type="text" autocomplete="off" placeholder="Exemplo: -8.290308">',
            '</div>',
            '</div>',
            '<div class="row"><div class="col s12 ha-left va-mid">',
            '<label for="address">Morada</label>',
            '<textarea name="address" autocomplete="off"></textarea>',
            '</div>',
            '</div>'
        ].join('');
    }

    function renderNewPartnerRow(partner){
        let newpartner = "";
        newpartner += '<div class="row partner" partner-id="'+partner.id+'">';
        newpartner += '<div class="col s1 ha-mid va-mid noselect">';
        newpartner += '<label for="toggle_check_partner_'+partner.id+'"><i class="material-icons">check_box_outline_blank</i></label>';
        newpartner += '<input type="checkbox" id="toggle_check_partner_'+partner.id+'">';
        newpartner += '</div>';
        /*
        newpartner += '<div class="col s2 ha-left va-mid">';
        if(partner.logo_img.type === 'url')
            newpartner += '<img src="{{ p.logo_img.src }}" alt="Logo '+partner.name+'">';
        else if(partner.logo_img.type === 'static')
            newpartner += '<img src="/static/partner_logos/'+partner.id+'.jpg" alt="Logo '+partner.name+'">';
        else
            newpartner += '<img src="/static/partner_logos/no_pic.jpg" alt="Logo '+partner.name+'">';
        newpartner += '</div>';
        */
        newpartner += '<div class="col s4 ha-left va-mid">'+partner.name+'</div>';
        newpartner += '<div class="col s4 ha-left va-mid"><a href="'+partner.url+'" target="_blank">'+partner.url+'</a></div>';
        newpartner += '<div class="col s3 ha-mid va-mid noselect">';
        newpartner += '<i class="material-icons partner_option" data-action="edit" title="Editar informação de parceria">edit</i>\n';
        newpartner += '<i class="material-icons partner_option" data-action="delete" title="Apagar parceria">delete</i>\n';
        newpartner += '<i class="material-icons partner_option" data-action="hide" title="Desactivar parceria">visibility_off</i>\n';
        newpartner += '</div></div>';
        return newpartner;
    }

    function addNewSpot(){
        $.get('/get_spot_types', function(res){
            if(res.code === 1){
                vex.dialog.open({
                message: 'Adicionar Local',
                input: renderNewSpotForm(res.spot_types),
                buttons: [
                    $.extend({}, vex.dialog.buttons.YES, {text: 'Criar'}),
                    $.extend({}, vex.dialog.buttons.NO, {text: 'Cancelar'})
                ],
                callback: function(data){
                    if(data) {
                        if(typeof data['types'] === 'undefined'){
                            data['types'] = [];
                        }
                        $.ajax({
                            url: '/save_new_spot',
                            type: 'POST',
                            data: JSON.stringify(data),
                            processData: false,
                            contentType: "application/json; charset=utf-8",
                            dataType: "json",
                            success: function (res) {
                                console.log(res);
                                if(res.code === 1){
                                    window.location.reload(true);
                                }
                            }
                        });
                    }
                }
            });
            }
        });
    }

    function addNewPartner(){
        vex.dialog.open({
            message: 'Criar Novo Parceiro',
            input: renderNewPartnerForm(),
            buttons: [
                $.extend({}, vex.dialog.buttons.YES, {text: 'Criar'}),
                $.extend({}, vex.dialog.buttons.NO, {text: 'Cancelar'})
            ],
            callback: function (data) {
                if(data){
                    if (data.name.length > 0) {
                        let formdata = new FormData();
                        formdata.append('name', data.name);
                        if(typeof data.desc === 'undefined' || (typeof data.desc !== 'undefined' && data.desc.length === 0))
                            formdata.append('desc', null);
                        else
                            formdata.append('desc', data.desc);

                        let lat_reg = new RegExp("^(\\+|-)?(?:90(?:(?:\\.0{1,6})?)|(?:[0-9]|[1-8][0-9])(?:(?:\\.[0-9]{1,6})?))$");
                        let lng_reg = new RegExp("^(\\+|-)?(?:180(?:(?:\\.0{1,6})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\\.[0-9]{1,6})?))$");
                        let lat = null, lng = null;

                        if(typeof data.lat !== 'undefined' && lat_reg.exec(data.lat)){
                            lat = data.lat;
                        }
                        if(typeof data.lng !== 'undefined' && lng_reg.exec(data.lng)){
                            lng = data.lng;
                        }
                        formdata.append('gps', JSON.stringify({'lat': lat, 'lng': lng}));

                        if(typeof data.address === 'undefined' || (typeof data.address !== 'undefined' && data.address.length === 0))
                            formdata.append('address', null);
                        else
                            formdata.append('address', data.address);

                        if(typeof data.link === 'undefined' || (typeof data.link !== 'undefined' && data.link.length === 0))
                            formdata.append('url', null);
                        else
                            formdata.append('url', data.link);

                        let imtype = $('input[type="radio"][name="image_type_chooser"]:checked').val();

                        if(imtype === 'url'){
                            let url = $('#new_partner_img_url').val();
                            if(url.length > 0) {
                                formdata.append('img_url', url);
                            }
                            else {
                                imtype = 'none';
                            }
                        }
                        else if(imtype === 'static'){
                            let file = $('#new_partner_file_input')[0].files[0];
                            if(typeof file !== 'undefined' && file.type.match(/image.*/)){
                                if(window.FileReader){
                                    let reader = new FileReader();
                                    reader.readAsDataURL(file);
                                    console.log("fiz append de um ficheiro");
                                    formdata.append('pic', file);
                                }
                            } else {
                                imtype = 'none';
                            }
                        }
                        formdata.append('imgtype', imtype);

                        $.ajax({
                            url: '/add_partner',
                            type: 'POST',
                            data: formdata,
                            processData: false,
                            contentType: false,
                            xhrFields: {withCredentials: true},
                            success: function(res){
                                if(res.code === 1){
                                    $('#active_partners').append(renderNewPartnerRow(res.partner));
                                    vex.dialog.alert({message:'Parceiro adicionado'});
                                } else {
                                    vex.dialog.alert({message:'Ocorreu um erro ao adicionar um novo parceiro, por favor tente mais tarde'});
                                }
                            }
                        });
                    }
                }
            }
        });
    }

    function sendPartnerActionToServer(info){
        $.ajax({
            url: '/admin_partner_action',
            type: 'POST',
            data: JSON.stringify({'ids': info['ids'], 'action': info['action']}),
            processData: false,
            contentType: "application/json; charset=utf-8",
            dataType : "json",
            success: function(res){
                if(res.code === 1){
                    let table;
                    $.each(info['ids'], function(i, id){
                        if(i===0)
                            table = $('.row.partner[partner-id="'+id+'"]').parent();
                        if(res.action === 'delete')
                            $('.row.partner[partner-id="'+id+'"]').remove();
                        else if(res.action === 'show'){
                            let row = $($('.row.partner[partner-id="'+id+'"]').detach());
                            row.appendTo('#active_partners');
                            row.find('input[type="checkbox"]').prop('checked', false).trigger('change');
                            row.find('.partner_option[data-action="show"]').text('visibility_off').attr('data-action', 'hide');
                        }
                        else if(res.action === 'hide'){
                            let row = $($('.row.partner[partner-id="'+id+'"]').detach());
                            row.appendTo('#inactive_partners');
                            row.find('input[type="checkbox"]').prop('checked', false).trigger('change');
                            row.find('.partner_option[data-action="hide"]').text('visibility').attr('data-action', 'show');
                        }
                    });

                    table.find('input[type="checkbox"]:checked').prop('checked', false).change();
                    table.find('label').each(function(){
                        $(this).find('.material-icons').text('check_box_outline_blank');
                    });
                    table.find('.general_option').removeClass('active');

                    if(info['ids'].length > 1)
                        vex.dialog.alert({message: 'Estado dos parceiros selecionados alterado com sucesso'});
                    else if(info['ids'].length === 1)
                        vex.dialog.alert({message: 'Estado do parceiro selecionado alterado com sucesso'});
                }
                else if(res.code === -1){
                    vex.dialog.alert({
                        message: 'Ocorreu um erro ao tentar realizar a operação, por favor tente mais tarde.'
                    });
                }
                else {
                    vex.dialog.alert({
                        message: 'Acção inválida ou não tem autorização para realizar esta operação'
                    });
                }
            }
        });
    }

    function sendSpotActionToServer(info){
        console.log(info);
        $.ajax({
            url: '/admin_spot_action',
            type: 'POST',
            data: JSON.stringify(info),
            processData: false,
            contentType: "application/json; charset=utf-8",
            dataType : "json",
            success: function(res){
                if(res.code === 1){
                    let table;
                    $.each(info['ids'], function(i, id){
                        let row = $('.row.spot[spot-id="'+id+'"]');
                        if(i===0)
                            table = $('.row.spot[spot-id="'+id+'"]').parent();
                        if(res.action === 'delete'){
                            row.remove();
                            $('.spot_info[for="'+id+'"]').remove();
                        }
                        else if(res.action === 'show'){
                            row.attr('data-state', 'active');
                            row.find('input[type="checkbox"]').prop('checked', false).trigger('change');
                            row.find('.spot_option[data-action="show"]').text('visibility_off').attr('data-action', 'hide');
                        }
                        else if(res.action === 'hide'){
                            row.attr('data-state', 'inactive');
                            row.find('input[type="checkbox"]').prop('checked', false).trigger('change');
                            row.find('.spot_option[data-action="hide"]').text('visibility').attr('data-action', 'show');
                        }

                        $('#toggle_check_spot_'+id+'').prop('checked', false).change();
                        $('label[for="toggle_check_spot_'+id+'"]').find('.material-icons').text('check_box_outline_blank');
                    });

                    table.find('.general_option').removeClass('active');

                    if(info['ids'].length > 1)
                        vex.dialog.alert({message: 'Estado dos locais selecionados alterado com sucesso'});
                    else if(info['ids'].length === 1)
                        vex.dialog.alert({message: 'Estado do local selecionado alterado com sucesso'});
                }
                else if(res.code === -1){
                    vex.dialog.alert({
                        message: 'Ocorreu um erro ao realizar a operação, por favor tente mais tarde.'
                    });
                }
                else {
                    vex.dialog.alert({
                        message: 'Acção inválida ou não tem autorização para realizar esta operação'
                    });
                }
            }
        });
    }

    function sendUserActionToServer(info){
        $.ajax({
            url: '/admin_user_action',
            type: 'POST',
            data: JSON.stringify({'ids': info['ids'], 'action': info['action']}),
            processData: false,
            contentType: "application/json; charset=utf-8",
            dataType : "json",
            success: function(res){
                if(res.code === 1){
                    let table;
                    $.each(info['ids'], function(i, id){
                        if(i===0)
                            table = $('.row.user[user-id="'+id+'"]').parent();
                        if(res.action === 'delete')
                            $('.row.user[user-id="'+id+'"]').remove();
                        else if(res.action === 'unblock' || res.action === 'accept'){
                            let row = $($('.row.user[user-id="'+id+'"]').detach());
                            row.appendTo('#active_users');
                            row.find('input[type="checkbox"]').prop('checked', false).trigger('change');
                            if(res.action === 'unblock'){
                                row.find('.user_option[data-action="unblock"]').text('block').attr('data-action', 'block');
                            }
                            else if(res.action === 'accept'){
                                row.find('.user_option[data-action="accept"]').remove();
                            }
                        }
                        else if(res.action === 'block') {
                            let row = $($('.row.user[user-id="'+id+'"]').detach());
                            row.appendTo('#blocked_users');
                            row.find('input[type="checkbox"]').prop('checked', false).trigger('change');
                            row.find('.user_option[data-action="block"]').text('lock_open').attr('data-action', 'unblock');
                        }
                    });

                    table.find('input[type="checkbox"]:checked').prop('checked', false).change();
                    table.find('label').each(function(){
                        $(this).find('.material-icons').text('check_box_outline_blank');
                    });
                    table.find('.general_option').removeClass('active');

                    if(info['ids'].length > 1)
                        vex.dialog.alert({message: 'Estados dos utilizadores selecionados alterado com sucesso'});
                    else if(info['ids'].length === 1)
                        vex.dialog.alert({message: 'Estado do utilizador selecionado alterado com sucesso'});
                }
                else if(res.code === -1){
                    vex.dialog.alert({
                        message: 'Ocorreu um erro ao tentar realizar a operação, por favor tente mais tarde.'
                    });
                }
                else {
                    vex.dialog.alert({
                        message: 'Acção inválida ou não tem autorização para realizar esta operação'
                    });
                }
            }
        });
    }

    function userOptionClicked(){
        let my_action = $(this).attr('data-action');

        let info = {
            'ids': [parseInt($(this).parent().parent().attr('user-id'))],
            'action': my_action,
            'username': $(this).parent().parent().find('.col').eq(1).text(),
            'email': $(this).parent().parent().find('.col').eq(2).text(),
            'gender': $(this).parent().parent().find('.col').eq(3).text()
        };

        let message;
        switch (my_action){
            case 'delete':
                message = 'Quer mesmo APAGAR o utilizador "'+info['username']+'"?';
                break;
            case 'block':
                message = 'BLOQUEAR utilizador "'+info['username']+'"?';
                break;
            case 'unblock':
                message = 'DESBLOQUEAR utilizador "'+info['username']+'"?';
                break;
            case 'accept':
                message = 'ACEITAR utilizador "'+info['username']+'"?';
                break;
            default:
                console.log("user action not treated");
        }
        vex.dialog.confirm({
            'message': message,
            callback: function(choice){
                if(choice){
                    sendUserActionToServer(info);
                }
                return false;
            }
        });
    }

    function spotOptionClicked(){
        let id = parseInt($(this).parent().parent().attr('spot-id'));
        let action = $(this).attr('data-action');
        let spot_name = $(this).parent().parent().find('.col').eq(1).text();
        let info = {
            'ids': [id],
            'action': action
        };

        if(action === 'info'){
            let chosen = $('.spot_info[for="'+id+'"]');
            if(chosen.is(':visible')){
                chosen.hide().html("");
            } else {
                $('.spot_info').hide().html("");
                $.get('/get_spot_info/'+id, function(res){
                    if(res.code === 1){
                        chosen.html(renderSpotInfo(res.spot, res.spot_types));
                        chosen.show();
                    }
                });

            }
            return false;
        } else if(action === 'delete') {
            vex.dialog.confirm({
                'message': 'APAGAR ' + spot_name + '?',
                callback: function(choice){
                    if(choice){
                        sendSpotActionToServer(info);
                    }
                    return false;
                }
            });
        } else if(action === 'hide' || action === 'show') {
            sendSpotActionToServer(info);
        }
    }

    function renderSpotInfo(spot, spot_types){
        console.log(spot);
        let spot_info = '';
        spot_info += '<div class="row">';
        spot_info += '<div class="col s12 ha-left va-mid">';
        spot_info += '<div class="row">';
        spot_info += '<div class="col s8 va-top ha-left">';
        spot_info += '<label for="name_input_spot_'+ spot.id +'">Nome</label>';
        spot_info += '<input type="text" id="name_input_spot_'+ spot.id +'" readonly value="'+ spot['name']['pt'] +'" data-original="'+ spot['name']['pt'] +'">';
        spot_info += '</div><div class="col s4 va-top ha-right" spot-id="'+ spot.id +'">';
        spot_info += '<i class="material-icons spot_info_option" data-action="edit" title="Editar informação do local">edit</i>';
        spot_info += '<i class="material-icons spot_info_option" data-action="cancel" style="display:none;" title="Cancelar alterações">close</i>';
        spot_info += '<i class="material-icons spot_info_option" data-action="save" style="display:none;" title="Guardar alterações">save</i>';
        spot_info += '</div></div><div class="row"><div class="col s8 ha-left va-top">';
        spot_info += '<label for="desc_input_spot_'+ spot.id +'">Descrição</label>';
        spot_info += '<textarea id="desc_input_spot_'+ spot.id +'" readonly data-original="'+(typeof spot['description']['pt'] !== 'undefined' ? spot['description']['pt'] : "")+'">'+(typeof spot['description']['pt'] !== 'undefined' ? spot['description']['pt'] : "")+'</textarea>';
        spot_info += '</div>';
        spot_info += '<div class="col s4 ha-right va-top location">';
        spot_info += '<label for="location_input_spot_'+ spot.id +'">Localização</label>';
        spot_info += '<input type="text" id="location_input_spot_'+ spot.id +'" readonly value="'+ spot.location.lat +', '+ spot.location.lng +'" data-original="'+ spot.location.lat +', '+ spot.location.lng +'" placeholder="Exemplo: 41.517857, -8.319532">';
        spot_info += '</div></div>';
        spot_info += '<div class="spot_types noselect" data-spot-id="'+ spot.id +'" style="display: none;">';
        spot_info += '<div class="row">';
        spot_info += '<div class="col s12 ha-left va-mid"><label for="">Tipos</label></div>';
        spot_info += '</div>';
        let stypes = JSON.stringify(spot.types);
        $.each(spot_types, function(i, st){
            //console.log(stypes.indexOf(JSON.stringify(st)) > -1 ? st.name + " YES" : st.name + ' NO');
            spot_info += '<div class="spot_type" data-original-checked-value="'+(stypes.indexOf(JSON.stringify(st)) > -1 ? "yes" : "no")+'">';
            spot_info += '<input id="stype_'+ st.id +'_for_spot_'+ spot.id +'" class="spot_type_check" type="checkbox" value="'+st.id+'" '+(stypes.indexOf(JSON.stringify(st)) > -1 ? "checked" : "")+'>';
            spot_info += '<label for="stype_'+st.id+'_for_spot_'+ spot.id +'">';
            spot_info += '<i class="material-icons spot_type_icon">'+(stypes.indexOf(JSON.stringify(st)) > -1 ? "check_box" : "check_box_outline_blank")+'</i>'+st['name']['pt'];
            spot_info += '</label></div>';
        });
        spot_info += '</div>';
        spot_info += '<div class="row">';
        spot_info += '<div class="col s6 ha-left va-mid">Imagens</div>';
        spot_info += '<div class="col s6 ha-right va-mid" spot-id="'+ spot.id +'">';
        spot_info += '<i class="material-icons spot_image_option select" data-action="clear"';
        spot_info += 'style="display: none;" title="Limpar selecção">clear</i>';
        spot_info += '<i class="material-icons spot_image_option select" data-action="delete"';
        spot_info += 'style="display: none;" title="Apagar imagens selecionadas">delete</i>';
        spot_info += '<i class="material-icons spot_image_option" data-action="add"';
        spot_info += 'title="Adicionar imagens ao local">add_a_photo</i>';
        spot_info += '<input type="file" class="spot_image_file_input" id="image_input_'+ spot.id +'"';
        spot_info += 'name="file_'+ spot.id +'" accept="image/*" multiple style="display: none;">';
        spot_info += '</div></div><div class="spot_images noselect" data-spot-id="'+ spot.id +'">';
        $.each(spot.images, function(k, src){
            spot_info += '<div class="spot_image" data-src="'+src+'" style="background-image: url(\'/static/spot_imgs/'+ spot.id +'/'+src+'\');">';
            spot_info += '<div class="hover"></div></div>';
        });
        spot_info += '</div>';
        spot_info += '</div>';
        spot_info += '</div>';
        return spot_info;
    }

    function partnerOptionClicked(){
        let action = $(this).attr('data-action');
        let partner_name = $(this).parent().parent().find('.col').eq(1).text();
        let info = {
            'ids': [parseInt($(this).parent().parent().attr('partner-id'))],
            'action': action
        };

        if(action === 'edit'){
            editPartnerInfo(parseInt($(this).parent().parent().attr('partner-id')));
            return false;
        } else if(action === 'delete') {
            vex.dialog.confirm({
                'message': 'APAGAR parceria com ' + partner_name + '?',
                callback: function(choice){
                    if(choice){
                        sendPartnerActionToServer(info);
                    }
                    return false;
                }
            });
        } else {
            sendPartnerActionToServer(info);
        }
    }

    function generalPartnerOptionClicked(){
        let my_table = $(this).parent().parent().parent();
        let my_action = $(this).attr('data-action');
        let ids = [];
        my_table.find('.row:not(.title):not(.header)').each(function(){
            if($(this).find('input[type="checkbox"]').is(':checked')){
                ids[ids.length] = parseInt($(this).attr('partner-id'));
            }
        });
        let info = {
            'ids': ids,
            'action': my_action
        };

        let message;
        switch (my_action){
            case 'delete':
                message = 'Quer mesmo APAGAR os parceiros selecionados?';
                break;
            case 'hide':
                message = 'DESACTIVAR parceiros selecionados?';
                break;
            case 'show':
                message = 'ACTIVAR parceiros selecionados?';
                break;
            default:
                console.log("general partner action not treated");
        }
        vex.dialog.confirm({
            'message': message,
            callback: function(choice){
                if(choice){
                    sendPartnerActionToServer(info);
                }
                return false;
            }
        });
    }

    function generalSpotOptionClicked(){
        let my_action = $(this).attr('data-action');

        let ids = [];
        $('.row.spot').each(function(){
            if($(this).find('input[type="checkbox"]').is(':checked'))
                ids[ids.length] = parseInt($(this).attr('spot-id'));
        });

        let info = {
            'ids': ids,
            'action': my_action
        };
        let message;
        switch (my_action){
            case 'delete':
                message = 'Quer mesmo APAGAR os locais selecionados?';
                break;
            case 'hide':
                message = 'DESACTIVAR locais selecionados?';
                break;
            case 'show':
                message = 'ACTIVAR locais selecionados?';
                break;
            default:
                console.log("general spot action not treated");
        }
        vex.dialog.confirm({
            'message': message,
            callback: function(choice){
                if(choice){
                    sendSpotActionToServer(info);
                }
                return false;
            }
        });
    }

    function generalUserOptionClicked(){
        let my_table = $(this).parent().parent().parent();
        let my_action = $(this).attr('data-action');

        let ids = [];
        my_table.find('.row:not(.title):not(.header)').each(function(){
            if($(this).find('input[type="checkbox"]').is(':checked')){
                ids[ids.length] = parseInt($(this).attr('user-id'));
            }
        });
        let info = {
            'ids': ids,
            'action': my_action
        };

        let message;
        switch (my_action){
            case 'delete':
                message = 'Quer mesmo APAGAR os utilizadores selecionados?';
                break;
            case 'block':
                message = 'BLOQUEAR utilizadores selecionados?';
                break;
            case 'unblock':
                message = 'DESBLOQUEAR utilizadores selecionados?';
                break;
            case 'accept':
                message = 'ACEITAR utilizadores selecionados?';
                break;
            default:
                console.log("general user action not treated");
        }
        vex.dialog.confirm({
            'message': message,
            callback: function(choice){
                if(choice){
                    sendUserActionToServer(info);
                }
                return false;
            }
        });
    }

    function generalCheckBoxChanged(e) {
        e.stopImmediatePropagation();
        let changed_id = $(this).attr('id');
        let table = $('#'+$(this).attr('data-table')+'');
        let is_checked = $('#' + changed_id + '').is(':checked');

        if(table.length === 0){
            console.log("table doesn't exist");
        }

        let dependent_checkboxes;
        if(table.attr('id') === 'spots_list'){
            dependent_checkboxes = $('.row.spot .col:first-of-type input[type="checkbox"]');
        }
        else {
            dependent_checkboxes = table.find('.row:not(.title):not(.header)').find('input[type="checkbox"]');
        }


        dependent_checkboxes.each(function () {
            $(this).prop('checked', is_checked);
            $('label[for="'+$(this).attr('id')+'"]').find('.material-icons').text(is_checked ? 'check_box' : 'check_box_outline_blank');
        });

        if(is_checked && dependent_checkboxes.length > 0)
            $(this).parent().parent().parent().find('.row.title').find('.general_option').addClass('active');
        else
            $(this).parent().parent().parent().find('.row.title').find('.general_option').removeClass('active');

        $('label[for="'+changed_id+'"').find('.material-icons').text(is_checked ? 'check_box' : 'check_box_outline_blank');
    }

    function regularCheckBoxChanged() {
        let changed = $(this);

        let label = $('label[for="' + changed.attr('id') + '"]').find('.material-icons');
        if (changed.is(':checked'))
            label.text('check_box');
        else
            label.text('check_box_outline_blank');

        let general_cbox = $(this).parent().parent().parent().find('.header').find('input[type="checkbox"]');
        let general_label = $('label[for="'+general_cbox.attr('id')+'"]').find('.material-icons');
        let total = $(this).parent().parent().parent().find('.row:not(.title):not(.header)').find('input[type="checkbox"]').length;
        let checked = $(this).parent().parent().parent().find('.row:not(.title):not(.header)').find('input[type="checkbox"]:checked').length;

        if($(this).parent().parent().parent().attr('id') === 'spots_list'){
            total = $('.row.spot').find('input[type="checkbox"]').length;
            checked = $('.row.spot').find('input[type="checkbox"]:checked').length;
        }

        if (checked === total && total > 0){
            general_label.text('check_box');
            general_cbox.prop('checked', true);
            general_cbox.trigger('change');
        }
        else if(checked === 0){
            general_label.text('check_box_outline_blank');
            general_cbox.prop('checked', false);
            general_cbox.trigger('change');
        }
        else if(checked < total) {
            general_cbox.prop('checked', false);
            general_label.text('indeterminate_check_box');
        }

        if(checked > 0 && total > 0)
            $(this).parent().parent().parent().find('.row.title').find('.general_option').addClass('active');
        else
            $(this).parent().parent().parent().find('.row.title').find('.general_option').removeClass('active');
    }

    function toggleTables() {
        let value = $(this).attr('data-value');
        if ($(this).hasClass('pressed')) {
            $(this).removeClass('pressed');
            if(value === 'active_spots' || value === 'inactive_spots'){
                let chosen = value.replace('_spots', '');
                $('.row.spot').each(function(){
                    if($(this).attr('data-state') === chosen){
                        $(this, '.spot_info[for="'+$(this).attr('spot-id')+'"]').hide();
                    }
                });
                return false;
            }
            $('#' + value + '').hide();
        } else {
            $(this).addClass('pressed');
            if(value === 'active_spots' || value === 'inactive_spots'){
                let chosen = value.replace('_spots', '');
                $('.row.spot').each(function(){
                    if($(this).attr('data-state') === chosen){
                        $(this, '.spot_info[for="'+$(this).attr('spot-id')+'"]').show();
                    }
                });
                return false;
            }
            $('#' + value + '').show();
        }
    }

    function userLogin() {
        let cred = $('#login_credential').val();
        let pw = $('#login_password').val();

        if (cred.length * pw.length > 0) {
            let formdata = new FormData();
            formdata.append('credential', cred);
            formdata.append('password', pw);

            console.log(cred);
            console.log(pw);

            $.ajax({
                url: '/login',
                type: 'POST',
                data: formdata,
                processData: false,
                contentType: false,
                xhrFields: {withCredentials: true},
            }).done(function (res) {
                if (res.code === 0)
                    console.log(res.error);
                else if (res.code === 1) {
                    window.location.reload(true);
                }
            });
        }
        return false;
    }
});
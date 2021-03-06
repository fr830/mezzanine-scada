var svg_text_map=[];
var variable_array=[];
var variable_dict={};
var svg_boolean_indicator_map=[];
var svg_boolean_control_map=[];

function init_svg_text() {
    for (doc_i=0;doc_i<$('.scada_svg').length;doc_i++) {
        var svg_doc = $('.scada_svg')[doc_i].contentDocument;
        svg_text_map.push([]);
        //for each text in the schematic
        for (text_i=0;text_i<$('text',svg_doc).length;text_i++) {
            //if the text has the correct properties, add to the variable list
            try {
                if ($('text',svg_doc)[text_i].attributes.class.value.includes('scada_variable')) {
                    var_name=$('text',svg_doc)[text_i].attributes.variable.value;
                    var_id=$('text',svg_doc)[text_i].attributes.id.value;
                    if (!(variable_array.includes(var_name))) {
                        variable_array.push(var_name);
                        variable_dict[var_name]='';
                    }
                    svg_text_map[doc_i].push([var_id,var_name])
                }
            } catch(err) {
            } 
        }
    }
    //we can change the value of the text with:
    //svg_index=0; //this is the svg file index
    //text_index=0; //this is the index of the text item inside the svg file
    //my_value=value of my variable called svg_text_map[svg_index][text_index][1]
    //$('#'+svg_text_map[svg_index][text_index][0] ,$('.scada_svg')[svg_index].contentDocument).text(my_value)
}

function init_svg_boolean_indicators() {
    //the svg boolean indicators are shapes in a svg. 
    //a svg boolean indicator is linked to one variable. If it's >0.0 it is painted in one color and if it's <=0 it's painted in other color
    //also can be greyed if a state automaton is in one of a list of states.
    //for instance:
    //a shape with:
    //class:                   scada_boolean_indicator 
    //variable:                in_valve
    //true_color:              #00ff00
    //false_color:             #ff0000
    //state_machine_control:   tank_control
    //grey_states:             auto_on auto_off    
    //indicates a shape that will be green if the variable in_valve>0 or red if invalve<=0
    //the color will be greyed if the state machine controll called tank_control is in the state auto_on or auto_off
    for (doc_i=0;doc_i<$('.scada_svg').length;doc_i++) {
        var svg_doc = $('.scada_svg')[doc_i].contentDocument;
        svg_boolean_indicator_map.push([]);
        //for each shape in the schematic
        for (g_i=0;g_i<$('g',svg_doc).length;g_i++) {
            //if the graphic shape has the correct properties, add to the variable list
            try {
                if ($('g',svg_doc)[g_i].attributes.class.value.includes('scada_boolean_indicator')) {
                    var_name=$('g',svg_doc)[g_i].attributes.variable.value.replace(/ /g,'');
                    var_id=$('g',svg_doc)[g_i].attributes.id.value;
                    if (!(variable_array.includes(var_name))) {
                        variable_array.push(var_name);
                        variable_dict[var_name]='';
                    }
                    true_color=$('g',svg_doc)[g_i].attributes.true_color.value.replace(/ /g,'');
                    false_color=$('g',svg_doc)[g_i].attributes.false_color.value.replace(/ /g,'');
                    automaton=$('g',svg_doc)[g_i].attributes.state_machine_control.value.replace(/ /g,'');
                    grey_states=$('g',svg_doc)[g_i].attributes.grey_states.value.split(' ').filter(function(n) { return n.length>0; });
                    svg_boolean_indicator_map[doc_i].push({'id':var_id,
                                                           'name':var_name,
                                                           'true_color':true_color,
                                                           'false_color':false_color,
                                                           'automaton':automaton,
                                                           'states':grey_states});
                }
            } catch(err) {
            } 
        }
    }

}

function init_svg_boolean_controls() {
    //the svg boolean controllers are rectangles in a svg. 
    //a svg boolean controller is a rectangle that you can click.
    //usually is a rectangle almost transparent adobe other shapes. when the page loads it is invisible and when the mouse is over this shape, 
    //then it's visible. If the user click adobe this shape, then a command is sended to a state machine control and all the page colors and values
    //within the page are loaded again.
    //this shape has this attributes:
    //class:                   scada_boolean_control 
    //state_machine_control:   the name of a state machine control within the system. tank_control for instance
    //command:                 the command that is sended to the system. change_auto_status for instance     
    for (doc_i=0;doc_i<$('.scada_svg').length;doc_i++) {
        var svg_doc = $('.scada_svg')[doc_i].contentDocument;
        svg_boolean_control_map.push([]);
        //for each shape in the schematic
        for (bc_i=0;bc_i<$('rect',svg_doc).length;bc_i++) {
            //if the graphic shape has the correct properties, add to the variable list
            try {
                if ($('rect',svg_doc)[bc_i].attributes.class.value.includes('scada_boolean_control')) {
                    var_command=$('rect',svg_doc)[bc_i].attributes.command.value.replace(/ /g,'');
                    var_id=$('rect',svg_doc)[bc_i].attributes.id.value;
                    automaton=$('rect',svg_doc)[bc_i].attributes.state_machine_control.value.replace(/ /g,'');
                    var_fill=$('#'+var_id,svg_doc).css('fill');
                    var_stroke=$('#'+var_id,svg_doc).css('stroke');
                    svg_boolean_control_map[doc_i].push({'id':var_id,
                                                         'automaton':automaton,
                                                         'command':var_command,
                                                         'stroke':var_stroke,
                                                         'fill':var_fill});
                    //save the colors in the element itself
                    $('#'+var_id,svg_doc)[0].init_stroke=var_stroke;
                    $('#'+var_id,svg_doc)[0].init_fill=var_fill;
                    //hide the element
                    $('#'+var_id,svg_doc).css('stroke','none');
                    $('#'+var_id,svg_doc).css('fill','transparent'); 
                    //add a hover effect
                    $('#'+var_id,svg_doc).hover(function() { 
                        $(this).css('stroke',$(this)[0].init_stroke);
                        $(this).css('fill',$(this)[0].init_fill);
//                        for (doc_i=0;doc_i<svg_boolean_control_map.length;doc_i++) {
//                            for (bc_i=0;bc_i<svg_boolean_control_map[doc_i].length;bc_i++) {
//                                if (svg_boolean_control_map[doc_i][bc_i]['id']==$(this)[0].id) {
//                                    $(this).css('stroke',svg_boolean_control_map[doc_i][bc_i]['stroke']);
//                                    $(this).css('fill',svg_boolean_control_map[doc_i][bc_i]['fill']);
//                                    $(this).css('stroke',$(this)[0].init_stroke);
//                                    $(this).css('fill',$(this)[0].init_fill);
//                                }
//                            }
//                        }
                    },                          function() { 
                        $(this).css('stroke','none');
                        $(this).css('fill','transparent'); 
                    });
                    //add a function that is executed when the user click the rectangle
                    $('#'+var_id,svg_doc).click(function() { 
                        console.log('clicked. Call the automaton linked to this control');
                        console.log('automaton: '+$(this)[0].attributes.state_machine_control.value);
                        console.log('commando: '+$(this)[0].attributes.command.value);
                    });
                }
            } catch(err) {
            } 
        }
    }

}



function init_scada() {
    svg_text_map=[];
    variable_array=[];
    variable_dict={};
    init_svg_text();
    init_svg_boolean_indicators();
    init_svg_boolean_controls();

    refresh_scada();

}



function svg_text_to_page() {
    for (svg_index=0;svg_index<svg_text_map.length;svg_index++) {
        var svg_doc = $('.scada_svg')[svg_index].contentDocument;
        for (text_index=0;text_index<svg_text_map[svg_index].length;text_index++) {
            my_value=variable_dict[svg_text_map[svg_index][text_index][1]];
            $('#'+svg_text_map[svg_index][text_index][0] ,$('.scada_svg')[svg_index].contentDocument).text(my_value);
        }
    }
}

function svg_boolean_indicators_to_page() {
    for (svg_index=0;svg_index<svg_boolean_indicator_map.length;svg_index++) {
        var svg_doc = $('.scada_svg')[svg_index].contentDocument;
        for (g_index=0;g_index<svg_boolean_indicator_map[svg_index].length;g_index++) {
            my_value=variable_dict[svg_boolean_indicator_map[svg_index][g_index]['name']];
            my_color='#ffffff';
            try {
                if (my_value>0.0) {
                  my_color=svg_boolean_indicator_map[svg_index][g_index]['true_color']
                } else {
                  my_color=svg_boolean_indicator_map[svg_index][g_index]['false_color']
                }
            } catch(err) {}
            $('#'+svg_boolean_indicator_map[svg_index][g_index]['id'] ,svg_doc)[0].style.fill=my_color;
            for (child_i=0;child_i<$('#'+svg_boolean_indicator_map[svg_index][g_index]['id'] ,svg_doc)[0].children.length;child_i++) {
                try {
                    $('#'+svg_boolean_indicator_map[svg_index][g_index]['id'] ,svg_doc)[0].children[child_i].style.fill=my_color;
                } catch(err) {}
            }
        }
    }
}




function data_to_page() {
    svg_text_to_page();
    svg_boolean_indicators_to_page();
}



function refresh_scada() {
    //this function runs each 10s, TODO: use the metadata of the svg (the shortest one)
    setTimeout(refresh_scada,10000);

    //get the lastest values of the variables
    try {
        $.ajax({
            url: '/ajax/get_multiple_value/',
            data:  $.param({names: variable_array}),
            dataType: 'json',
            success: function (data) {
                try {
                    for (var_name in data) {
                        variable_dict[var_name]=data[var_name]['value']
                    
                    data_to_page();
                    }
                } catch(err) {
                    console.log('error in ajax:');
                    console.log(data);
                }
            }
          });

    } catch(err){
    }
    
}

$(window).on('load', function() { init_scada(); });
let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code
        componentRestrictions: {'country': ['in']},
    })
// function to specify what should happen when the prediction is clicked
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields
    console.log(place)
    var geocoder = new google.maps.Geocoder()
    var address = document.getElementById('id_address').value

    geocoder.geocode({'address': address}, function(results, status){
        if(status == google.maps.GeocoderStatus.OK){
            var latitude = results[0].geometry.location.lat() 
            var longitude = results[0].geometry.location.lng() 

            $('#id_latitude').val(latitude)
            $('#id_longitude').val(longitude)
            $('#id_address').val(address)
          
        }

    })
    // loop through the adderss component
    for(var i=0; i<place.address_components.length; i++){
        for(var j=0; j<place.address_components[i].types.length; j++){
            // get country
            if(place.address_components[i].types[j] == 'country'){
                $('#id_country').val(place.address_components[i].long_name)
            }
            //get state
            if(place.address_components[i].types[j] == 'administrative_area_level_1'){
                $('#id_state').val(place.address_components[i].long_name)
            }
            //get city
            if(place.address_components[i].types[j] == 'locality'){
                $('#id_city').val(place.address_components[i].long_name)
            }
            //get pincode
            if(place.address_components[i].types[j] == 'postal_code'){
                $('#id_pincode').val(place.address_components[i].long_name)//j-query
            }
            else{
                $('#id_pincode').val("")//for not having pincode
            }
        }
    }
}


$(document).ready(function(){

    // add to cart 

    $('.add_to_cart').on('click', function(e){
        e.preventDefault();
        
        food_id = $(this).attr('data-id')
        url = $(this).attr('data-url')

        
        $.ajax({
            type:'GET',
            url:url,
            
            success:function(response){
                console.log(response)
                if (response.status == 'login_required'){
                    swal(response.message,'','info').then(function(){
                        window.location = '/login'
                    })
                }

                else if (response.status == 'Failed'){
                    swal(response.message,'','error')
                    
                }
                else{
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty)
                    applyCartAmount(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total']
                    )
                }
                
            } 
        })
    })

    //place the item quantity

    $('.item_qty').each(function(){
        var the_id = $(this).attr('id')
        var qty = $(this).attr('data-qty')
        console.log(qty)
        $('#'+the_id).html(qty)

    })

    // decrease cart
    
    $('.decrease_cart').on('click', function(e){
        e.preventDefault();
        
        food_id = $(this).attr('data-id')
        url = $(this).attr('data-url')
        cart_id = $(this).attr('id')
        $.ajax({
            type:'GET',
            url:url,
            
            success:function(response){
                console.log(response)

                if (response.status == 'login_required'){
                    swal(response.message,'','info').then(function(){
                        window.location = '/login'
                    })
                }

                else if (response.status == 'Failed'){
                    swal(response.message,'','error')
                }

                else{
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    $('#qty-'+food_id).html(response.qty)
                    applyCartAmount(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total']
                    )
                    removeCartItem(response.qty, cart_id)
                    checkEmptycart()
                }
                
            } 
        })
    })

    // Delete cart item
    $('.delete_cart').on('click', function(e){
        e.preventDefault();
        
        cart_id = $(this).attr('data-id')
        url = $(this).attr('data-url')

        

        $.ajax({
            type:'GET',
            url:url,
            
            success:function(response){
                console.log(response)

                if (response.status == 'Failed'){
                    swal(response.message,'','error')
                }
                else{
                    $('#cart_counter').html(response.cart_counter['cart_count'])
                    swal(response.status,response.message,'success')
                    
                    if(window.location.pathname == '/cart/'){
                        removeCartItem(0, cart_id)
                        checkEmptycart()
                        applyCartAmount(
                            response.cart_amount['subtotal'],
                            response.cart_amount['tax_dict'],
                            response.cart_amount['grand_total']
                        )
                    }
                    
                }
                
            } 
        })
    })

    // delete the cart element if quantity is 0
    function removeCartItem(CartItemQty, cart_id){
        if (CartItemQty <= 0){
            // remove the cart item element
            document.getElementById("cart-item-"+cart_id).remove()
        }

    }

    function checkEmptycart(){
        var cart_counter = document.getElementById('cart_counter').innerHTML
        if (cart_counter == 0){
            document.getElementById('empty-cart').style.display="block"
        }
    }

    function applyCartAmount(subtotal, tax_dict, grand_total){
        if(window.location.pathname == '/cart/'){
        $('#subtotal').html(subtotal)
        $('#total').html(grand_total)

        for(tax_name in tax_dict){
            // console.log(tax_name)
            for(tax_percentage_amount in tax_dict[tax_name]){
                // console.log(tax_dict[tax_name][tax_percentage_amount])
                $('#tax-'+tax_name).html(tax_dict[tax_name][tax_percentage_amount])
            }
        }
    }}

    // add opening hours
    $('.add_hour').on('click', function(e){
        e.preventDefault();
        var day = document.getElementById('id_day').value;
        var from_hours = document.getElementById('id_from_hours').value;
        var to_hours = document.getElementById('id_to_hours').value;
        var is_holiday = document.getElementById('id_is_holiday').checked;
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val()
        var url = document.getElementById('add_hour_url').value;

        condition = "day != ''  &&  from_hours != '' && to_hours != ''"
        // console.log(day, from_hours,to_hours,is_holiday)

        if (eval(condition)){
            // console.log('i am evaluated')
           $.ajax({
                type: 'POST',
                url:url,
                data:{
                    'day':day,
                    'from_hours':from_hours,
                    'to_hours': to_hours,
                    'is_holiday': is_holiday,
                    'csrfmiddlewaretoken': csrf_token,
                },
                success: function(response){
                    if(response.status == 'success'){
                        if(response.is_holiday == 'True') {
                            html = '<tr id="hour-' + response.id + '"><td class="text-danger"><b>' + response.day + '</b></td><td class="text-danger"><b>' + response.from_hours + ' - ' + response.to_hours + ' &nbsp;(Closed)</b></td><td><b><a href="#" class="text-success remove_hour" data-url="/vendor/opening-hours/delete/' + response.id + '/">Remove</a></b></td></tr>';
                            swal(response.message,'','success')
                            
                        } 
                        else {
                            console.log("ellighebandhe bro")
                            html = '<tr id="hour-' + response.id + '"><td class="text-success"><b>' + response.day + '</b></td><td class="text-success"><b>' + response.from_hours + ' - ' + response.to_hours + ' &nbsp;</b></td><td><b><a href="#" class="text-success remove_hour" data-url="/vendor/opening-hours/delete/' + response.id + '/">Remove</a></b></td></tr>';
                            swal(response.message,'','success')
                            
                        }
                          
                         $('.opening_hours').append(html)
                        document.getElementById('opening_hours').reset()
                    }
                    else if(response.status == 'Exist'){
                        document.getElementById('opening_hours').reset()
                        swal(response.message,'','info')

                    }
                    else if(response.status == 'max'){
                        $('.opening_hours').append(html)
                        document.getElementById('opening_hours').reset()
                        swal(response.message,'','info')

                    }
                    
                    else{
                        $('.opening_hours').append(html)
                        document.getElementById('opening_hours').reset()
                        swal(response.message,'','error')
                    }
                }


           })
        }else{
            swal("Please fill all fields", '', 'info')
        }
        
    });

    // delete opening hours
    $(document).on('click', '.remove_hour', function (e) {
        e.preventDefault();
        url = $(this).attr('data-url');
        $.ajax({
            type: 'GET',
            url: url,
            success:function(response){
                if (response.status == 'success'){
                    document.getElementById('hour-'+response.id).remove()
                }
            }
        })


    });


    // below is document ready close
});


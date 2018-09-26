

$(function () {
    $('#SendOrder').click(function () {
        var product_account = $('#product_account').val();
        var type = $('#orderType').val();
        var symbol = $('#symbol').val();
        var price = $('#price').val();
        var volumn = $('#volumn').val();
        if( symbol=='' || price=='' || volumn ==''){
            alert('Error Fields..');
            return;
        }
        alert(product_account+' | ' + type +' | ' + symbol + " | " +
            price + " | " + volumn + " | " + url );
        sendOrder(url,product_account,symbol,price,type,volumn);
        // alert(JSON.stringify(orderIds));
    });

    // 撤销委托单
    $('#CancelOrder').click(function () {
        var product_account = $('#product_account').val();
        var orderId = $('#orderId').val();
        if( orderId == ''){
            alert('Need Order ID .. ');
            return ;
        }
        cancelOrder(product_account,orderId);
    });

    // 撤销所有委托单（指定账号)
    $('#CancelAllOrders').click(function () {
        var product_account = $('#product_account').val();
        cancelAllOrders(product_account);
    });

    // 撤销所有委托单
     $('#CancelAllOrdersIgnoreAccount').click(function () {
        CancelAllOrdersIgnoreAccount();
    });
     // 一键平仓
     $('#SellOrBuyCoverAll').click(function () {
        SellOrBuyCoverAll();
    });


})();

function sendOrder(url,product_account,symbol,price,type,volumn) {
    $.ajax({
        url: url+'/orders',
        type: 'post',
        // dataType: 'json',
        async: true,
        data: {product_account:product_account,symbol: symbol, price: price, volumn: volumn, type: type}
    }).done(function (data) {
            alert("当前访问:" + JSON.stringify(data));
            return;

            // if(data.status == 0){
            //
            // }else{
            //     alert("当前访问Eror:"+ JSON.stringify(data) );
            // }
        });
}

function cancelOrder(product_account,orderId) {
    // 撤单
    $.ajax({
        url: url+'/orders',
        type: 'delete',
        // dataType: 'json',
        async: true,
        data: {product_account: product_account, order_id: orderId}
    }).done(function (data) {
            alert("当前访问:" + JSON.stringify(data));
            return;
        });
}

function cancelAllOrders(product_account) {
    // 撤全单
     $.ajax({
        url: url+'/orders/all',
        type: 'delete',
        // dataType: 'json',
        async: true,
        data: {product_account: product_account}
    }).done(function (data) {
        alert("当前访问:" + JSON.stringify(data));
    });

}

function CancelAllOrdersIgnoreAccount() {
    // 撤所有账户下的委托单
     $.ajax({
        url: url+'/orders/all/ignore_account',
        type: 'delete',
        // dataType: 'json',
        async: true
    }).done(function (data) {
        alert("当前访问:" + JSON.stringify(data));
    });

}

function  SellOrBuyCoverAll() {
    // 一键平仓（市场限价平掉所有仓位)
    $.ajax({
        url: url+'/positions/empty',
        type: 'post',
        // dataType: 'json',
        async: true
    }).done(function (data) {
        alert("当前访问:" + JSON.stringify(data));
    });

}
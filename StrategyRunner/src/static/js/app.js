/*
*	@file 配置文件
*	@time 20170214
*/
'usr strict';
$('.trackAnalysisHeader div').on('click',function(){
    if($(this).index() == 0 || $(this).index() == 1){
        //轨迹纠偏
        TrackAnalysis.handleToggleProcess($(this),$(this).index());
    }else{
        //驾驶行为分析
        TrackAnalysis.handleToggleBehavior($(this),$(this).index());
    }
});
//关闭轨迹纠偏或者驾驶分析详细选择项
$('.processClose,.behaviorClose').on('click',function(){
    TrackAnalysis.handleClose($(this));
});
//开启轨迹纠偏
$('.processSwitchOff').on('click',function(){
    TrackAnalysis.handleProcessSwitch();
});
//开启驾驶行为分析
$('.behaviorSwitchOff').on('click',function(){
    TrackAnalysis.handleBehaviorSwitch();
});
//开启轨迹纠偏或者驾驶行为分析后checkbox的选择子类
$('.processControl ins,.behaviorControl ins').on('click',function(){
    TrackAnalysis.setCheckboxStyle($(this).siblings('input').attr('id'),$(this));
});
//时间轴
timeline.initTimeCount();
$('.timelineMain').append(timeline.addtimeLine());
$('.timelineMain').append(timeline.addtimeNumber());
$('.timelineMain').append(timeline.addtimelineProgress());
$('.timelinePlay').on('click',function(e){
    var e = e||event;
    timeline.handlePlayOrPause(e);
});
$('.timelineSlow').on('click',function(e){
    var e = e||event;
    timeline.handleSlow(e);
});
$('.timelineQuick').on('click',function(e){
    var e = e||event;
    timeline.handleQuick(e);
});
$('.timelineMain').on('click',function(e){
    var e = e||event;
    timeline.handleJumpTime(e);
});
var handle = false;

$('.timelineMain .timelineProgress').on('mousedown',function(e){
    if($('#datetimepicker_start .datetimeInput').val() == '' || $('#datetimepicker_end .datetimeInput').val() == '' || $('.searchInputMonitor_2').val() == ''){
        return;
    }else{
        var e = e||event;
        handle = true;
        timeline.handleProgressDragStart(e);
    }
}).on('mouseup',function(e){
    var e = e||event;
    timeline.onMouseUp(e)
});
$(document).mousemove(function(e){
    var e = e||event;
    if(handle){
        timeline.onDrag(e);
    }
});
$(document).mouseup(function(){
    handle = false;
});
tracksearch.initTrackDatetime();
tracksearch.selectPlateSim();
$('.searchButton').on('click',function(e){
    var e = e||event;
    tracksearch.searchTrack('searchButton');
});
$('.resetButton').on('click',function(){
    tracksearch.onReset();
});
function GetQueryString(name)
{
     var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
     var r = window.location.search.substr(1).match(reg);
     if(r!=null)return  unescape(r[2]); return null;
}
var start = GetQueryString('start');
var plate = GetQueryString('plate');
if(start !== null && plate != null){
    $('#datetimepicker_start input').val(new Date(start*1000).format('yyyy-MM-dd 00:00:00'));
    $('#datetimepicker_end input').val(new Date(start*1000).format('yyyy-MM-dd hh:mm:ss'));
    $('.searchInputMonitor_2').val(plate);
    setTimeout('$(".searchButton").trigger("click")',1000);
}

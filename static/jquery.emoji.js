var i = 1;
$.fn.emoji = function() {
	alert($(this).html());
	return this.each(function(){
		$(this).html(
			$(this).html().replace(/([\ue001-\ue537])/g, $.fn.emoji.replacer)
		);
	});
};

$.fn.emoji.replacer = function (str, p1) {
	return p1.charCodeAt(0).toString(16).toUpperCase().replace(
		/^([\da-f]+)$/i,
		'<img src="/static/emoji/emoji-$1.png" alt="emoji" />'
	);
}
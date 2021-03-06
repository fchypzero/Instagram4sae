/** 
 * imglazyload v1.1 for jQuery
 * Author : chenmnkken@gmail.com
 * Url : http://stylechen.com/imglazyload2.html
 * Date : 2012-03-29
 */
(function(d){d.fn.imglazyload=function(k){var e=d.extend({attr:"lazy-src",container:window,event:"scroll",fadeIn:false,threshold:0,vertical:true},k);k=e.event;var l=e.vertical,c=d(e.container),o=e.threshold,i=d.makeArray(d(this)),u=l?"top":"left",p=l?"scrollTop":"scrollLeft",q=l?c.height():c.width(),r=c[p](),v=q+r,w={init:function(a){return a>=r&&a<=v+o},scroll:function(a){var b=c[p]();return a>=b&&a<=q+b+o},resize:function(a){var b=c[p](),g=l?c.height():c.width();return a>=b&&a<=g+b+o}},t=function(a,
b){var g=0,s=false,h,m,f,n;if(b){if(b!=="scroll"&&b!=="resize")s=true}else b="init";for(;g<i.length;g++){m=i[g];f=d(m);n=f.attr(e.attr);if(!(!n||m.src===n)){h=f.data("imglazyload_offset");if(h===undefined){h=f.offset()[u];f.data("imglazyload_offset",h)}if(h=s||w[b](h)){m.src=n;e.fadeIn&&f.hide().fadeIn();f.removeData("imglazyload_offset");i.splice(g--,1)}}}if(!i.length){a?a.unbind(b,j):c.unbind(e.event,j);d(window).unbind("resize",j);i=null}},j=function(a){t(d(this),a.type)};c=k==="scroll"?c:d(this);
c.bind(k,j);d(window).bind("resize",j);t();return this}})(jQuery);
<?php 

require_once('qiniu/rs.php');
require_once('qiniu/http.php');
require_once('qiniu/auth_digest.php');
require_once('qiniu/utils.php');


$accessKey = '';
$secretKey = '';
Qiniu_SetKeys($accessKey, $secretKey);
$mac = new Qiniu_Mac($accessKey, $secretKey);

$url = "http://t-test2.qiniudn.com/t1.mp3?p/2/avthumb/mp/ar/44100/ab/32k";

$size = strlen($url);
#$accessToken = Qiniu_Sign(null, $url);
$accessToken = $mac->Sign("/t1.mp3?p/2/avthumb/mp/ar/44100/ab/32k\n");

echo $accessToken . "\n";

$u = array('path' => $url);
$req = new Qiniu_Request($u, null);
$req->Header['Authorization'] = "QBox $accessToken";
$req->Header['Content-Type'] = "application/x-www-form-urlencoded";
$req->Header['Content-Length'] = "0";
echo 'start' . "\n";
$ret = Qiniu_Client_do($req);
var_dump($ret);

?>

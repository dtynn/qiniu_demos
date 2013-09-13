<?php 

require_once('qiniu/rs.php');
require_once('qiniu/http.php');
require_once('qiniu/auth_digest.php');


$accessKey = 'iguImegxd6hbwF8J6ij2dlLIgycyU4thjg-xmu9q';
$secretKey = 'EXJInB-eR0nkOwFet9uwP89MNzSpNXVqBoSh1yBo';
Qiniu_SetKeys($accessKey, $secretKey);

$url = 'http://t-test2.qiniudn.com/t1.mp3?p/2/avthumb/mp3/ar/44100/ab/32k';
$size = strlen($url);
#$ret = Qiniu_Client_Call($client, $url);
$accessToken = Qiniu_Sign(null, $url);
echo $accessToken . "\n";

$u = array('path' => $url);
$req = new Qiniu_Request($u, null);
$req->Header['Authorization'] = "QBox $accessToken";
$req->Header['Content-Length'] = "0";
echo 'start' . "\n";
$ret = Qiniu_Client_do($req);
var_dump($ret);

?>

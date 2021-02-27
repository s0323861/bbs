#!/usr/local/bin/perl
# =====================================================
# 分類：スマホ対応のフリー掲示板
# 名前：index.cgi
# 機能：掲示板の記事一覧表示
# 作者：A.Mukai
# 参照：http://s0323861.moo.jp/bbs/
# =====================================================

use Time::Local;
use Encode qw(is_utf8);
use CGI qw(:standard);
use File::Basename;
use Jcode;

# データファイル
my $bbsfile = "data.csv";

# RSSファイル
my $rssfile = "template.xml";

# ベースデザインファイル
my $base = "base.html";

# 書き込み部分デザインファイル
my $lay = "lay.html";

# Logの最大件数
my $logline = "5000";

# 1ページの表示件数
my $line = "10";

# 同一IPによる連続書き込み禁止時間（秒数）
my $dubble = "180";

# 入力パラメータの取得
my $title = param("title");
my $bun = param("bun");
my $name = param("name");
my $mail = param("mail");
my $start = param("start");
my $res = param("res");

if($title eq ""){
	$title = "(無題)";
}

my $agent = $ENV{'HTTP_USER_AGENT'};

my $website = "http://" . $ENV{'HTTP_HOST'} . $ENV{'REQUEST_URI'};
$website = (fileparse($website))[1];

# 携帯電話からのアクセス
if ($agent =~ /(DoCoMo|J-PHONE|Vodafone|SoftBank|KDDI|UP.Browser|WILLCOM)/){

	$agent = "phone";

# スマートフォンからのアクセス
}elsif($agent =~ /(iPod|iPhone|Android)/){

	$agent = "mobile";

# PCからのアクセス
}else{

	$agent = "pc";

}

# ホスト名を取得
my $remote_host = &GetHostByAddr($ENV{'REMOTE_ADDR'});

# IPアドレスを取得
my $remote_ip = $ENV{'REMOTE_ADDR'};

# 参照アドレスを取得
my $ref = $ENV{'HTTP_REFERER'};

# 書き込み処理
if($bun ne "" and $name ne "") {

	# 1970年1月1日からの経過秒数を返す
	$date = time;

	&open($bbsfile);
	($no,$ipadd,$email,$day) = (split(/\t/,@all[0]))[0,1,4,7];

	# 連続書き込みの禁止（IPアドレスのチェック）
	if($ipadd eq $remote_ip and $date < $day + $dubble){
		$error = $error . "連続しての書き込みは禁止されてます<br>";
	}

	# 連続書き込みの禁止（Eメールアドレスのチェック）
	if($mail ne "" and $mail eq $email and $date < $day + $dubble){
		$error = $error . "連続しての書き込みは禁止されてます<br>";
	}

	if($error eq ""){

		$no++;

		$write = "$no!--yokohama--$remote_ip!--yokohama--$name!--yokohama--$title!--yokohama--$mail!--yokohama--$url!--yokohama--$bun!--yokohama--$date!--yokohama--$remote_host!--yokohama--$ref";

		$write =~s/<[^>]*>//g;

		# CR+LFをCRに変換
		$write =~ s/\r\n/\r/g;
		# LFをCRに変換
		$write =~ s/\n/\r/g;
		# 改行コードはCRに統一後にbrに変換
		$write =~ s/\r/<br>/g;

		# タブをスペースに変換
		$write =~ s/\t/ /g;

		$write =~ s/!--yokohama--/\t/g;

		$kazu = @all;
		if ($kazu > $logline){
			$#all--;
		}
		push(@up, @all);
		unshift(@up, $write . "\n");

		&write($bbsfile);

		&writeRSS;

		print "Location: index.cgi?\n\n";

	}else{
		$log .= "<h3 class=\"text-danger\">エラー</h3>\n";
		$log .= "<p>$error</p>\n";
		$log .= "<p><a href=\"./?\">戻る</a></p>\n";
	}
	undef(@all);
	undef(@up);
}

# ページ制御
if($error eq "") {

	open(IN, "$lay");
	while(<IN>){
		$laybase .= $_;
	}
	close(IN);

	&open($bbsfile);
	$kazu = @all;
	if($kazu eq ""){
		$kazu = 0;
	}

	if($start eq ""){
		$start = 0;
	}

	$end = $start + $line;

	if($end >= $kazu){
		$end = $kazu;
	}else{
		$next = "<a href=\"index.cgi?start=" . $end . "\">Older &rarr;</a>";
	}

	if($start != 0){
		$old = $start - $line;
		$back = "<a href=\"index.cgi?start=" . $old . "\">&larr; Newer</a>";
	}

	$pagekazu = int(($kazu-1)/$line);

	if($pagekazu != 0) {
		$page = <<EOT;
                <ul class="pager">
                    <li class="previous">
                        $back
                    </li>
                    <li class="next">
                        $next
                    </li>
                </ul>
EOT

	}

	for ($z = $start; $z < $end; $z++) {
		($no,$ip,$name,$title,$mail,$url,$bun,$date,$remote_host,$ref) = (split(/\t/,@all[$z]));
		$layout = $laybase;
		($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime($date);
		$year = $year + 1900;
		$mon++;
		@week = ('日','月','火','水','木','金','土');
		$wday = @week[$wday];
		$day = "$year年$mon月$mday日($wday)$hour時$min分$sec秒";


		if($mail ne ""){
			$name = "<a href=\"mailto:$mail\">$name</a>";
		}

		if($url ne ""){
			$url = "<p><a href=\"$url\">$url</a></p>";
		}

		$reply = "index.cgi?res=" . $no;

		if($res == $no){
			$sub = $title;
			$r_sub = "Re:$sub";
			$com = $bun;
			$r_com = "&gt; $com";
			$r_com =~ s/<br>/\r&gt; /ig;
			$r_com =~ s/<a href=\"(.*)\"(.*)>(.*)<\/a>/$1/g;
		}

		$layout =~ s/<!--name-->/$name/ig;
		$layout =~ s/<!--bun-->/$bun/ig;
		$layout =~ s/<!--date-->/$day/ig;
		$layout =~ s/<!--rhost-->/$remote_host/ig;
		$layout =~ s/<!--title-->/$title/ig;
		$layout =~ s/<!--url-->/$url/ig;
		$layout =~ s/<!--reply-->/$reply/ig;
		$log = $log . $layout;
	}

}

open(IN, "$base");
while(<IN>){
	$buffer.= $_;
}
close(IN);

$buffer =~ s/<!--daimei-->/$r_sub/ig;
$buffer =~ s/<!--naiyou-->/$r_com/ig;
$buffer =~ s/<!--title-->/$titlename/ig;
$buffer =~ s/<!--log-->/$log/ig;
$buffer =~ s/<!--line-->/$line/ig;
$buffer =~ s/<!--page-->/$page/ig;

print header( -type => 'text/html',-charset => 'UTF-8');
print $buffer;

exit;

#-------------------------------------------------
# ファイルを開く
#-------------------------------------------------
sub open {
	open(IN,$_[0]);
	flock(IN, 1);
	@all = <IN>;
	close(IN);
}

#-------------------------------------------------
# ファイル書き込み
#-------------------------------------------------
sub write {
	open(OUT, ">".$_[0]);
	flock(OUT, 2);
	# データサイズを0にする
	truncate(OUT, 0);
	# ファイルの先頭に移動する
	seek(OUT, 0, 0);
	foreach (@up){
		print OUT $_;
	}
	flock(OUT, 8);
	close(OUT);
}

#-------------------------------------------------
# リモートホスト取得
#-------------------------------------------------
sub GetHostByAddr {
	my($ip_address) = @_;
	my(@addr) = split(/\./, $ip_address);
	my($packed_addr) = pack("C4", $addr[0], $addr[1], $addr[2], $addr[3]);
	my($name, $aliases, $addrtype, $length, @addrs);
	($name, $aliases, $addrtype, $length, @addrs) = gethostbyaddr($packed_addr, 2);
	if($name eq ""){
		$name = $ip_address;
	}
	return $name;
}

#-------------------------------------------------
# RSSファイルの作成
#-------------------------------------------------
sub writeRSS {

	open(IN, "$rssfile");
	while(<IN>){
		$buffer .= $_;
	}
	close(IN);

	my $lastmodified = (stat $bbsfile)[9];

	# 日付のフォーマット修正
	($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime($lastmodified);
	$year = $year + 1900;
	# $mon++;
	@month = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec');
	$mon = @month[$mon];
	@week = ('Sun','Mon','Tue','Wed','Thu','Fri','Sat');
	$wday = @week[$wday];

	# 0埋め
	my $jikan = sprintf("%02d:%02d:%02d", $hour, $min, $sec);
	my $hiniti = sprintf("%02d", $mday) . " " . $mon . " " . $year;

	$day = "$wday, $hiniti $jikan +0900";

	$description = $bun;

	$buffer =~ s/<!--url-->/$website/ig;
	$buffer =~ s/<!--update-->/$day/ig;
	$buffer =~ s/<!--title-->/$title/ig;
	$buffer =~ s/<!--description-->/$description/ig;
	$buffer =~ s/<!--date-->/$day/ig;

	open(OUT, ">rss.xml");
	flock(OUT, 2);

	# データサイズを0にする
	truncate(OUT, 0);
	# ファイルの先頭に移動する
	seek(OUT, 0, 0);

	# ファイルへ書き込む
	print OUT $buffer;

	flock(OUT, 8);
	close(OUT);

}

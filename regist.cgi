#!/usr/bin/perl

use Encode qw(is_utf8);
use CGI qw(:standard);
use Jcode;

# データファイル
$bbsfile = "data.csv";

# 管理者ID
$username = "test";

# 管理者パスワード
$password = "test";

# 1ページの表示件数
$line = "20";

# 入力チェック
my $user = param("user");
my $pass = param("pass");
my $id = param("id");
my $delno = param("delno");
my $start = param("start");

print header( -type => 'text/html',-charset => 'UTF-8');

if ($user eq $username and $pass eq $password){
	if ($id eq "delete"){
		&delete;
	}else{
		&login;
	}
}

# Loginページ

&head;
print <<"EOF";
  <!-- Forms
  ================================================== -->
        <div class="well bs-component">
          <form class="form-horizontal" data-toggle="validator" method="post" action="./regist.cgi">
            <fieldset>
              <div class="form-group">
                <label for="inputName" class="col-lg-2 control-label">ユーザー名</label>
                <div class="col-lg-10">
                  <input type="text" class="form-control" id="inputName" placeholder="Name" name="user" required>
                </div>
              </div>
              <div class="form-group">
                <label for="inputPass" class="col-lg-2 control-label">パスワード</label>
                <div class="col-lg-10">
                  <input type="password" class="form-control" id="inputPass" placeholder="Password" name="pass" required>
                </div>
              </div>
              <div class="form-group">
                <div class="col-lg-10 col-lg-offset-2">
                  <button type="submit" class="btn btn-primary">ログイン</button>
                  <button type="reset" class="btn btn-default">キャンセル</button>
                </div>
              </div>
            </fieldset>
          </form>
        </div>

EOF
&footer;

#-------------------------------------------------
# 書き込み削除
#-------------------------------------------------
sub delete {

	&open($bbsfile);

	foreach $mun (@all){
		($no,$ip,$name,$title,$mail,$url,$bun,$date,$rhost,$ref) = (split(/\t/,$mun));
		if($delno eq $no){
			&add("delete.csv", $mun);
		}else{
			push (@up,$mun);
		}
	}

	&write($bbsfile);

	&head;

	print <<"EOF";
	<h3>指定の書き込みを削除しました。</h3>

	<p>
	<a href="regist.cgi?user=$user&pass=$pass">一覧に戻る</a><br>
	</p>
EOF

	&footer;

}

#-------------------------------------------------
# ページ表示
#-------------------------------------------------
sub login{

	&head;

	&open($bbsfile);

	$kazu = @all;

	if($kazu eq ""){
		$kazu = 0;
	}

	if($start eq ""){
		$start = "0";
	}

	$end = $start + $line;

	if($end >= $kazu){
		$end = $kazu;
	}else{
		$next = <<"EOL";
		<a href="regist.cgi?user=$username&pass=$password&start=$end">Older &rarr;</a>
EOL
	}

	if($start ne "0"){
		$old = $start - $line;
		$back = <<"EOL";
		<a href="regist.cgi?user=$username&pass=$password&start=$old">&larr; Newer</a>
EOL
	}

	$pagekazu = int(($kazu-1)/$line);

	if($pagekazu ne "0"){
		for ($p = 0; $p <= $pagekazu; $p++){
			$pagestart = $p*$line;
			$pp = $p+1;
			if($pagestart eq $start){
				$page = $page."$pp";
			}else{
				$page = $page."<a href=\"regist.cgi?user=$user&pass=$pass&start=$pagestart\">$pp</a>";
			}

			if($p < $pagekazu){
				$page = $page." ";
			}
		}

		#print "$back $page $next<hr>";

	}

	for ($z = $start; $z < $end; $z++){
		($no,$ip,$name,$title,$mail,$url,$bun,$date,$rhost,$ref) = (split(/\t/,@all[$z]));
		$layout = $laybase;
		($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime($date);
		$year=$year+1900;
		$mon++;
		$day = "$year年$mon月$mday日$hour時$min分$sec秒";

		if($mail ne ""){
			$name = "<a href=\"mailto:$mail\">$name</a>";
		}

		if($url ne ""){
			$url = "<p><a href=\"$url\">$url</a></p>";
		}

		print <<"EOF";
		<h2>$title</h2>
		<p class="lead">by $name</p><p><span class="glyphicon glyphicon-time"></span> Posted on $day</p>
		<p>$bun<br>
		<form name="form1" method="post" action="regist.cgi">
		<input type="hidden" name="user" value=$user>
		<input type="hidden" name="pass" value=$pass>
		<input type="hidden" name="id" value="delete">
		<input type="hidden" name="delno" value="$no">
		<button type="submit" class="btn btn-danger pull-right" name="Submit"><span class="glyphicon glyphicon-trash"></span> 削除</button>
		</form>
		$url $rhost</p>
		<hr>
EOF
	}

		print <<"EOT";
                <ul class="pager">
                    <li class="previous">
                        $back
                    </li>
                    <li class="next">
                        $next
                    </li>
                </ul>
EOT

	&footer;

}


#-------------------------------------------------
# ファイルを開く
#-------------------------------------------------
sub open{
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
	truncate(OUT, 0);
	seek(OUT, 0, 0);
	foreach (@up){
		print OUT $_;
	}
	flock(OUT, 8);
	close(OUT);
}

#-------------------------------------------------
# ファイル書き込み（追記）
#-------------------------------------------------
sub add {
	open(OUT, ">>".$_[0]);
	flock(OUT, 2);
	# ファイルの末尾に移動する
	seek(OUT, 0, 2);
	print OUT $_[1];
	flock(OUT, 8);
	close(OUT);
}

# ページヘッダー
sub head {
	print <<"EOF";
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <title>フリー掲示板 管理画面</title>

  <link rel="stylesheet" type="text/css" href="./css/bootstrap.css">
  <style type="text/css">
  body { padding-top: 80px; }
  \@media ( min-width: 768px ) {
    #banner {
      min-height: 300px;
      border-bottom: none;
    }
    .bs-docs-section {
      margin-top: 8em;
    }
    .bs-component {
      position: relative;
    }
    .bs-component .modal {
      position: relative;
      top: auto;
      right: auto;
      left: auto;
      bottom: auto;
      z-index: 1;
      display: block;
    }
    .bs-component .modal-dialog {
      width: 90%;
    }
    .bs-component .popover {
      position: relative;
      display: inline-block;
      width: 220px;
      margin: 20px;
    }
    .nav-tabs {
      margin-bottom: 15px;
    }
    .progress {
      margin-bottom: 10px;
    }
  }
  </style>

  <!--[if lt IE 9]>
    <script src="//oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
    <script src="//oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
  <![endif]-->

</head>
<body>

<header>
  <div class="navbar navbar-default navbar-fixed-top">
    <div class="container">
      <div class="navbar-header">
        <a href="/" class="navbar-brand">Top</a>
        <button class="navbar-toggle" type="button" data-toggle="collapse" data-target="#navbar-main">
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
          <span class="icon-bar"></span>
        </button>
      </div>
      <div class="navbar-collapse collapse" id="navbar-main">
        <ul class="nav navbar-nav">
          <li><a href="./">掲示板</a></li>
        </ul>
      </div>
    </div>
  </div>
</header>

<div class="container">

        <div class="row">

            <!-- Blog Entries Column -->
            <div class="col-md-8">

                <h1 class="page-header">
                    掲示板
                    <small>投稿の削除を行います。</small>
                </h1>




EOF
}

# ページフッター
sub footer {
	print <<"EOF";

            </div>

            <!-- Blog Sidebar Widgets Column -->
            <div class="col-md-4">

                <!-- Blog Categories Well -->
                <div class="well">
                    <h4>メニュー</h4>
                    <div class="row">
                        <div class="col-lg-6">
                            <ul class="list-unstyled">
                                <li><a href="./">Top</a></li>
                                <li><a href="regist.cgi">管理画面</a></li>
                            </ul>
                        </div>
                        <!-- /.col-lg-6 -->
                    </div>
                    <!-- /.row -->
                </div>

                <!-- Blog Categories Well -->
                <div class="well">
                    <h4>注意事項</h4>
                    <div class="row">
                        <div class="col-lg-6">
                            <ul class="list-unstyled">
                                <li>初期ユーザー名とパスワードは「test」です。</li>
                            </ul>
                        </div>
                        <!-- /.col-lg-6 -->
                    </div>
                    <!-- /.row -->
                </div>

            </div>

        </div>
        <!-- /.row -->

        <hr>

        <!-- Footer -->
        <footer>
            <div class="row">
                <div class="col-lg-12">
                    <p>Copyright &copy; Akira Mukai 2015</p>
                </div>
                <!-- /.col-lg-12 -->
            </div>
            <!-- /.row -->
        </footer>

</div>


<script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
<script src="./js/bootstrap.min.js"></script>
<script src="./js/validator.js"></script>

<script type="text/javascript">
  \$('.bs-component [data-toggle="popover"]').popover();
  \$('.bs-component [data-toggle="tooltip"]').tooltip();
</script>

</body>
</html>
EOF
exit;
}

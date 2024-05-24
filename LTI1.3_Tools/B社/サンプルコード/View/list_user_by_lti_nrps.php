<!DOCTYPE html>
<html lang="ja">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="./js/sample.js" defer></script>    
    </head>
    <body>
        <div>
            <header>
                <div class="mx-auto py-2 px-4 sm:px-6 lg:px-8">
                    <h2 class="text-2xl text-white leading-tight ">
                        ユーザー情報
                    </h2>
                </div>
            </header>
        </div>
        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8 px-1">
                <table class="table-auto border">
                    <thead>
                        <tr>
                            <th class="border">ID</th>
                            <th class="border">name</th>
                        </tr>
                    </thead>
                    <tbody>
                        
                    </tbody>
                </table>
                
                <div class="mt-12 flex justify-center md:justify-start">
                    <button type="button" id="user_show_btn" data-launch="{{$launch}}" class='inline-flex items-center px-7 py-2 bg-blue-400 rounded font-semibold text-2xl text-white uppercase tracking-widest hover:bg-blue-700 active:bg-blue-700'>表示</button>
                </div>
            </div>
        </div>
    </body>
</html>

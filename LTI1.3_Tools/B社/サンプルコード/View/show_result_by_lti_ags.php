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
                        成績表
                    </h2>
                </div>
            </header>
        </div>
        <div class="py-12">
            <div id='result_list' class="max-w-7xl mx-auto sm:px-6 lg:px-8 px-1 mb-4 hidden">
                <table class="table-auto border text-center">
                    <thead>
                        <tr>
                            <th class="border px-2">ID</th>
                            <th class="border px-2">score</th>
                            <th class="border px-2">time</th>
                            <th class="border px-2">progress</th>
                        </tr>
                    </thead>
                    <tbody>
                        
                    </tbody>
                </table>
            </div>
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8 px-1">
                <p class="font-bold">成績を送る</p>
                <form name="myscore" class="rounded bg-gray-200 px-6 py-6 mb-4 w-full max-w-xs">
                    <input type="hidden" name="launch_id" value="{{$launch}}">
                    <div >
                        <label for="score" class="block font-bold">score: </label>
                        <input type="number" min="0" max="100" name="score" id="score" class="rounded w-full py-2 px-3">
                    </div>
                    <div>
                        <label for="course" class="block font-bold">course: </label>
                        <input type="text" name="course" id="course" class="rounded w-full py-2 px-3">
                    </div>
                    <div>
                        <label for="time" class="block font-bold">time: </label>
                        <input type="number" min="0" name="time" id="time" class="rounded w-full py-2 px-3">
                    </div>
                    <div>
                        <label for="progress" class="block font-bold">progress: </label>
                        <input type="number" step="0.01" min="0" max="100" name="progress" id="progress" class="rounded w-full py-2 px-3">
                    </div>
                    
                    <div class="mt-2 flex justify-center ">
                        <button type="button" id="score_btn" class='inline-flex items-center px-7 py-2 bg-blue-400 rounded font-semibold text-2xl text-white uppercase tracking-widest hover:bg-blue-700 active:bg-blue-700'>SCORE</button>
                    </div>
                </form>
            
                <p class="font-bold">成績を確認する</p>

                <form name="results" class="rounded bg-gray-200 px-6 py-6 mb-4 w-full max-w-xs">
                    <input type="hidden" name="launch_id" value="{{$launch}}">
                    <div>
                        <label for="course" class="block font-bold">course: </label>
                        <input type="text" name="course" id="course" class="rounded w-full py-2 px-3">
                    </div>
                    <div class="mt-2 flex justify-center ">
                        <button type="button" id="result_btn" class='inline-flex items-center px-7 py-2 bg-blue-400 rounded font-semibold text-2xl text-white uppercase tracking-widest hover:bg-blue-700 active:bg-blue-700'>RESULT</button>
                    </div>
                </form>
            </div>
        </div>
    </body>
</html>

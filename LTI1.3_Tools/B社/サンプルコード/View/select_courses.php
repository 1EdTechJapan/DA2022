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
                        コースを選択して下さい
                    </h2>
                </div>
            </header>
        </div>

        <div class="py-12">
            <div class="max-w-7xl mx-auto sm:px-6 lg:px-8 px-1">
                
                <form action='deeplink_response' method="POST" >
                    <input type="hidden" name='launch' value="{{$launch}}">                
                    <div class="container mx-auto xl:w-3/5 lg:w-4/5">
                    <?php 
                        foreach( $courses as $key => $course ){ ?>
                            <div class="mb-4">;                        
                            <input type='radio' name='course' id="course_<?php echo $key ?>" value="<?php $course['id'] ?>" class='hidden peer'>
                                <label for="course_<?php $key ?>" class="block py-4 border border-gray-400 rounded-md text-center cursor-pointer peer-checked:border-brix_orange">
                                <span class="px-1 tracking-wider text-2xl"><?php $course['name'] ?></span>
                                </label>
                            </div>
                    <?php  } ?>
                             
                    </div>
                    <div class="mt-12 flex justify-center md:justify-end">
                        <button disabled type="submit" class='inline-flex items-center px-7 py-2 bg-blue-400 rounded font-semibold text-2xl text-white uppercase tracking-widest hover:bg-blue-700 active:bg-blue-700 disabled:bg-gray-400'>決定</button>
                    </div>
                </form>
            </div>
        </div>
    </body>
</html>
    



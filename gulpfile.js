let gulp = require('gulp');
let print = require('gulp-print');



let sass = require('gulp-sass');
const SCSS_FILES = './sktimeline/static/scss/*.scss';
gulp.task('sass', function () {
  gulp.src(SCSS_FILES)
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('./sktimeline/static/css'));
});

gulp.task('sass:watch', function () {
  gulp.watch(SCSS_FILES, ['sass']);
})


let babel = require('gulp-babel');
const JS_FILES_TO_BUILD ='./sktimeline/static/js/_for-build/*.js';
gulp.task('js', function() {
  return gulp.src(JS_FILES_TO_BUILD)
      .pipe(print())  // todo: need to figure out error handler here
      .pipe(babel({ presets: ['es2015'] }))    // transpile ES2015 to ES5 using ES2015 preset
      .pipe(gulp.dest('./sktimeline/static/js/build'));  // copy the results to the build folder
});

gulp.task('js:watch', function () {
  gulp.watch(JS_FILES_TO_BUILD, ['js']);
})
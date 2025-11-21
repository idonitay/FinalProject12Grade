import * as sass from 'sass';
import * as fs from 'fs';

try
{
    const result = sass.compile('scss/styles.scss');
    fs.writeFileSync('css/styles.css', result.css);
    console.log('SCSS compiled successfully!');
}
catch (error)
{
    console.error('Error compiling SCSS:', error);
}
from unidiff import PatchSet
import io
import sys
import os
import enum

class LineType(enum.Enum):
    Add = 1
    Rem = 2
    Empty = 3
    Both = 4
    Special = 5

css_styles = '''
    * {
        box-sizing: border-box;
    }
    .container {
        box-shadow: 0px 0px 5px #000;
        margin-bottom: 50px;
        margin-top: 50px;
        border-radius: 10px;
        overflow: hidden;
        background-color: #eee;
    }
    .container > .row:first-child {
        height: 30px;
    }
    .container > .row:nth-child(2) > .column .line-number,
    .container > .row:nth-child(2) > .column .content {
        box-shadow: inset 0px 5px 5px -5px #000;
    }
    pre {
        padding: 0;
        margin: 0;
        white-space: break-spaces;
        word-break: break-word;
    }
    .row > .column:first-child{
        border-right: 1px solid #bbb;
    }
    .row {
        width: 100%;
        display: table;
    }
    .row > .column:first-child {
        left: 0;
    }
    .row > .column:nth-child(2) {
        right: 0;
    }
    .special {
        width: 100%;
        text-align: center;
        height: 24px;
        line-height: 24px;
        background-color: #eee;
        border-top: 1px solid #bbb;
        border-bottom: 1px solid #bbb;
    }
    .column {
        width: 50%;
        display: table-cell;
        vertical-align:top;
    }
    .column > div {
        display: table;
        width: 100%;
    }
    .header {
        padding-left: calc(5% + 3px);
        text-align: left;
        font-family: monospace;
        font-weight: normal;
        font-size: 12pt;
        background-color: #fff;
        height: 30px;
        line-height: 30px;
    }
    .line-number {
        width: 10%;
        display: table-cell;
        background-color: #eee;
        text-align: right;
        padding-right: 10px;
        vertical-align:top;
    }
    .content {
        display: table-cell;
        width: 90%;
        padding-left: 3px;
        vertical-align:top;
        background-color: #fff;
    }
    body {
        background-color: #eee;
        width: 100vw;
        font-size: 12pt;
        font-family: monospace;
    }
    body > div {
        width: 80%;
        margin: 0 auto;
    }
    .content.empty {
        background-color: #eee;
    }
    .after .line-number.added {
        background-color: rgb(191, 242, 191);
    }
    .before .line-number.removed {
        background-color: rgb(242, 191, 191);
    }
    .after .content.added {
        background-color: rgb(228, 255, 228);
    }
    .before .content.removed {
        background-color: rgb(255, 228, 228);
    }
'''



def convert_string_for_html(string):
    return string.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')



def convert_to_html(patches_before, patches_after):
    html_str = '<html><head><meta charset="UTF-8"><style>' + css_styles + '</style></head><body><div>'

    for patch_index in range(0, len(patches_before)):
        html_str += '<div class="container"><div class="row"><div class="column header">'
        html_str += patches_before[patch_index][0]
        html_str += '</div><div class="column header">'
        html_str += patches_after[patch_index][0]
        html_str += '</div></div>'

        for hunk_index in range(0, len(patches_before[patch_index][1])):
            for line_index in range(0, len(patches_before[patch_index][1][hunk_index])):
                html_str += '<div class="row">'
                line_before = patches_before[patch_index][1][hunk_index][line_index]
                line_after = patches_after[patch_index][1][hunk_index][line_index]

                if line_before[0] == None:
                    html_str += '<div class="special">'
                    html_str += convert_string_for_html(line_before[2])
                    html_str += '</div></div>'
                    continue

                element_class = 'line-number'
                element_class += ' removed' if line_before[1] == LineType.Rem else ''
                element_class += ' empty' if line_before[1] == LineType.Empty else ''
                html_str += '<div class="column before"><div><div class="' + element_class + '">'
                html_str += str(line_before[0]) if line_before[1] != LineType.Empty else ''

                element_class = 'content'
                element_class += ' removed' if line_before[1] == LineType.Rem else ''
                element_class += ' empty' if line_before[1] == LineType.Empty else ''
                html_str += '</div><div class="' + element_class + '"><pre>'
                html_str += convert_string_for_html(line_before[2])
                html_str += '</pre></div></div></div>'

                element_class = 'line-number'
                element_class += ' added' if line_after[1] == LineType.Add else ''
                element_class += ' empty' if line_after[1] == LineType.Empty else ''
                html_str += '<div class="column after"><div><div class="' + element_class + '">'
                html_str += str(line_after[0]) if line_after[1] != LineType.Empty else ''
                
                element_class = 'content'
                element_class += ' added' if line_after[1] == LineType.Add else ''
                element_class += ' empty' if line_after[1] == LineType.Empty else ''
                html_str += '</div><div class="' + element_class + '"><pre>'
                html_str += convert_string_for_html(line_after[2])
                html_str += '</pre></div></div></div></div>'

        html_str += '</div>'

    html_str += '</div></body></html>'

    return html_str



def parse_diff(diff):
    patch_set = PatchSet(diff)

    patches_before = []
    patches_after = []

    for patched_file in patch_set:
        file_before = []
        patches_before.append((patched_file.source_file, file_before))
        file_after = []
        patches_after.append((patched_file.target_file, file_after))

        for hunk in patched_file:
            if len(file_before):
                file_before[-1].append((None, LineType.Special, '. . . . .'))
                file_after[-1].append((None, LineType.Special, '. . . . .'))
            add_after = []
            hunk_before = []
            file_before.append(hunk_before)
            hunk_after = []
            file_after.append(hunk_after)

            for line in hunk:
                if line.line_type == '+':
                    value = (line.target_line_no, LineType.Add, line.value)
                    if len(hunk_before) and hunk_before[-1][1] == LineType.Rem and hunk_after[-1][1] == LineType.Empty:
                        try:
                            index = len(hunk_after) - 1
                            while (hunk_after[index][1] == LineType.Empty):
                                index -= 1
                            hunk_after[index + 1] = value
                        except Exception as e:
                            pass
                    else:
                        hunk_after.append(value)
                        hunk_before.append((0, LineType.Empty, ''))

                elif line.line_type == '-':
                    value = (line.source_line_no, LineType.Rem, line.value)
                    if len(hunk_after) and hunk_after[-1][1] == LineType.Add and hunk_before[-1][1] == LineType.Empty:
                        index = len(hunk_before) - 1
                        while (hunk_before[index][1] == LineType.Empty):
                            index -= 1
                        hunk_before[index + 1] = value
                    else:
                        hunk_before.append(value)
                        hunk_after.append((0, LineType.Empty, ''))
                elif line.source_line_no == None:
                    add_after.append((None, LineType.Special, line.value))
                else:
                    hunk_before.append((line.source_line_no, LineType.Both, line.value))
                    hunk_after.append((line.target_line_no, LineType.Both, line.value))
        
            for line in add_after:
                hunk_before.append(line)
                hunk_after.append(line)
    
    return patches_before, patches_after



def main():
    diff = ''
    for raw_line in sys.stdin.buffer:
        try:
            line = raw_line.decode('utf-8')
        except UnicodeDecodeError:
            line = raw_line.decode('cp1251')

        diff += line

    patches_before, patches_after = parse_diff(diff)
    html_str = convert_to_html(patches_before, patches_after)

    if len(sys.argv) > 1 and sys.argv[1] == '-f':
        with io.open('./diff.html', 'wb') as f:
            f.write(html_str.encode('utf-8'))
    else:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stdout.write(html_str)

if __name__ == '__main__':
    main()

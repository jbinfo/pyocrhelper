**This page describes how pyocrhelper analyses html page layout output by ocropus.**

---


**What does a line of content from Ocropus look like?**

When Ocropus analyses an image, it scans on a line per line basis. Thus, the html output by Ocropus is very line intensive in nature. A typical Ocropus content line looks something like:

```
   <span class='ocr_line' title='bbox 237 371 2058 412'>I am a line of Ocropus content</span>
```

From the above, the text `'I am a line of Ocropus content'` is exactly the text which was present in the image - i.e. what the reader will eventually read.

From looking at the <span> tag, it is possible to see that Ocropus usefully outputs some positional information for us. This positional information does not seem to be used in the html markup (Ocropus could possibly use css formatting which might make use of the bbox but I'm not sure about this). As far as I can tell, using the above example:<br>
<br>
<ul><li>237 is the leftmost x coordinate<br>
</li><li>371 is the topmost y coordinate<br>
</li><li>2058 is the rightmost x coordinate<br>
</li><li>412 is the bottommost y coordinate</li></ul>

<pre><code>237,371<br>
       +--------------------------------+<br>
       | I am a line of Ocropus content |<br>
       +--------------------------------+ 2058,412<br>
</code></pre>


<b>Analysing the layout of a typical Ocropus html page</b>

<hr />

If we split the html string output from pyocrhelper (or Ocropus for that matter) into lines, we can examine each line individually and feed the data into an array/list (which we can later analyse more completely). Thus (from pyocrhelper.py):<br>
<br>
<pre><code>    def _getCoordinates(self,string):<br>
        """<br>
        Use a regular expression to extract the page coordinates<br>
        from a typical hOcr string<br>
        """<br>
        # split this into multiple lines<br>
        getdigits = re.compile(r'bbox\s+?(?P&lt;pos1&gt;\d{1,4})\s+?\<br>
                    (?P&lt;pos2&gt;\d{1,4})\s+?(?P&lt;pos3&gt;\d{1,4})\s+?\<br>
                    (?P&lt;pos4&gt;\d{1,4})',re.S)<br>
        a = re.search(getdigits,string)<br>
        if not a:<br>
            return None<br>
        else:<br>
            return (int(a.group('pos1')),int(a.group('pos2')),\<br>
                    int(a.group('pos3')),int(a.group('pos4')))<br>
<br>
hold_left_col = []<br>
content_line_match = re.compile(r'&lt;span.*&lt;/span&gt;',re.S)<br>
ocr_lines = ocropus_output.split('\n')<br>
bottom_y = 0 # contains value of bottommost y coord of previous line<br>
for line in ocr_lines:<br>
    if re.match(content_line_match,line):<br>
        coordinates = self._getCoordinates(line)<br>
        hold_left_col.append(coordinates[0]) # append leftmost x coord<br>
        if bottom_y &lt; coord_tup[1]:<br>
            if bottom_y != 0: gap.append(coordinates[1]-bottom_y)<br>
        bottom_y = coord_tup[3]<br>
print hold_left_col<br>
print<br>
print gap<br>
<br>
[796, 93, 203, 1811, 478, 476, 478, 478, 477, 477, 477, 477, <br>
477, 476, 476, 475, 516, 514, 513, 513, 514, 513, 513, 473, <br>
475, 475, 474, 476, 472, 474, 474, 475, 474, 474, 474, 472, <br>
471, 473, 473, 474, 473, 181, 1469, 1468, 1466, 1468, 1468, <br>
1467, 1468, 1465, 1467, 1467, 1467, 1465, 1466, 1466, 1467, <br>
1467, 1467, 1467, 1466, 1466, 1466, 1466, 1532, 1502, 1534, <br>
1502, 1502, 1499, 1501, 1501, 1534, 1500, 1501, 1501, 1501, <br>
1500, 1500, 1523]<br>
<br>
[195, 18, 19, 19, 19, 17, 67, 19, 19, 19, 19, 18, 60, 19, 19,<br>
20, 19, 19, 20, 60, 19, 19, 59, 19, 26, 19, 18, 18, 18, 19, <br>
18, 18, 18, 18, 19, 59, 19, 202, 19, 19, 19, 19, 18, 18, 18,<br>
18, 18, 19, 18, 19, 19, 18, 23, 18, 19, 18, 18, 19, 18, 59,<br>
18, 60, 19, 17, 18, 18, 18, 60, 18, 19, 18, 19, 25, 18, 68]<br>
<br>
</code></pre>

For the document above (a two column page of text), Ocropus recognised two 'main' column left boundaries - if we cancel out the 'noise', these are roughly the x coordinates ~477 and ~1470.<br>
Likewise, if we look at the gaps between the lines, we see that that the gaps frequency falls into two major groups:<br>
<ol><li>roughly 18<br>
</li><li>roughly 60<br>
There are, however, some much larger gaps also evident. If we could analyse the frequency properly, we would therefore break down the 'standard' gap into the following:<br>
</li><li>~18 must be a standard line break<br>
</li><li>~60 must be a standard paragraph break<br>
If we choose <b>not</b> to ignore the 'extreme' gaps we could also factor them into a group of their own. Depending on the quality of layout analysis required, this might or might not be useful.</li></ol>

<b>Using a blur algorithm to do cluster analysis on the coordinate list</b>
<hr />
Although for a human it may be quite clear from a list such as the list described above, that there really are only two predominant 'gaps' (at roughly 18 and roughly 60), for the python interpreter, this is not at all clear, so we somehow have to make it clear. The algorithm uses is a 'blur' algorithm which 'heaps' the clusters of coordinates into individual heaps or piles. It should then be possible to analyse the individual heaps to identify the main 'heaps' and their minimum, maximum and standard deviance. Consider the following code:<br>
<br>
<pre><code><br>
def weight(self,a,b,max):<br>
    d = 0.0<br>
    if max &lt;= 0:<br>
        if a == b: return 1<br>
        else: return 0<br>
    if a &gt; b: d = a-b<br>
    else: d = b-a<br>
<br>
    if d &gt;= max: return 0<br>
    else:<br>
        return float(1.0-(float(d)/float(max)))<br>
<br>
def blur(self,arr,factor=0.1):<br>
    lbound,hbound = min(arr),max(arr)<br>
    spread = int(0.5 * factor * (hbound-lbound))<br>
    slist = []<br>
    for x in range((lbound-spread),(hbound+spread)):<br>
        s = 0<br>
        for i in arr:<br>
            s += self.weight(x,i,spread)<br>
        slist.append((x,s))<br>
    return slist<br>
<br>
</code></pre>
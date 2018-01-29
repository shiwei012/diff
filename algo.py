#!/usr/bin/python
# -*- utf-8 -*-

def lcs(A, B):
	result = 0
	if len(A) is 0 or len(B) is 0:
		result
	elif A[0] == B[0]:
		result = 1 + lcs(A[1:len(A)], B[1:len(B)])
	else:
		result = max(lcs(A, B[1:len(B)]), lcs(A[1:len(A)], B))
	return result


def column(matrix, i):
    return [row[i] for row in matrix]


def calc_row_status_table(a, b):
	rst = {};
	i = 0;
	for x in range(len(a)):
		res = [0, -1]
		for y in range(i, len(b)):
			t = lcs(a[x], b[y])
			if res[0] < t:
				res[0] = t
				res[1] = y
		if res[0] > 0:
			rst[x] = [res[1], res[0]]
			i = res[1] + 1
	return rst

def calc_col_status_table(a, b):
	rst = {};
	i = 0;
	for x in range(len(a[0])):
		res = [0, -1]
		for y in range(i, len(b[0])):
			t = lcs(column(a, x), column(b, y))
			if res[0] < t:
				res[0] = t
				res[1] = y
		if res[0] > 0:
			rst[x] = [res[1], res[0]]
			i = res[1] + 1
	return rst

def calc_row_status(a, b):
	# 0 for normal, 1 for insert, -1 for delete
	row_convert_info = []
	rst = calc_row_status_table(a, b)
	x = 0
	for i in range(len(a)):
		t = rst.get(i, None)
		if t is None and i < len(a):
			row_convert_info.append(-1)
		elif t[0] <= i:
			row_convert_info.append(0)
			x = t[0]
		elif t[0] > i:
			for y in range(x + 1, t[0]):
				row_convert_info.append(1)
			row_convert_info.append(0)
			x = t[0]
	for j in range(x + 1, len(b)):
		row_convert_info.append(1)
	return row_convert_info, rst


def calc_col_status(a, b):
	# 0 for normal, 1 for insert, -1 for delete
	col_convert_info = []
	cst = calc_col_status_table(a, b)
	x = 0
	for i in range(max(len(a[0]), len(b[0]))):
		t = cst.get(i, None)
		if t is None and i < len(a):
			col_convert_info.append(-1)
		elif t[0] <= i:
			col_convert_info.append(0)
			x = t[0]
		elif t[0] > i:
			for y in range(x + 1, t[0]):
				col_convert_info.append(1)
			col_convert_info.append(0)
			x = t[0]
	for j in range(x + 1, len(b)):
		col_convert_info.append(1)
	return col_convert_info, cst


def get_diff_matrix(a, b):
	rs, rst = calc_row_status(a, b)
	cs, cst = calc_col_status(a, b)
	print rs, rst
	print cs, cst
	# cell {value:, color: w for white r for red b for blue y for yellow}
	ret_mat = []
	x = 0
	for i in range(len(rs)):
		row = []
		y = 0
		for j in range(len(cs)):
			cell = {}
			if rs[i] == 0:
				if cs[j] == 0:
					cell["value"] = a[x][y]
					cell["color"] = 'w' if a[x][y] == b[rst[x][0]][cst[y][0]] else 'y'
				elif cs[j] == -1:
					cell["value"] = a[x][y]
					cell["color"] = 'r'
				elif cs[j] == 1:
					cell["value"] = ''
					cell["color"] = 'b'
			if rs[i] == -1:
				if cs[j] == 0:
					cell["value"] = a[x][y]
					cell["color"] = 'r'
				elif cs[j] == -1:
					cell["value"] = ''
					cell["color"] = 'r'
				elif cs[j] == 1:
					cell["value"] = ''
					cell["color"] = 'b'
			if rs[i] == 1:
				if cs[j] == 0 or cs[j] == 1:
					cell["value"] = ''
					cell["color"] = 'b'
				elif cs[j] == -1:
					cell["value"] = ''
					cell["color"] = 'r'
			if cs[j] == 0 or cs[j] == -1:
				y = y + 1
			row.append(cell)
		if rs[i] == 0 or rs[i] == -1:
			x = x + 1
		ret_mat.append(row)
	return ret_mat



a = [
		['a', 'b', 'c'],
		['d', 'e', 'f'],
		['g', 'h', 'i'],
	]
b = [
		['a', 'b', 'c'],
		['d', 'e', 'f'],
		['x', 'y', 'j'],
	]


c = [
		['Col-1', 'Col-2', 'Col-3', 'Col-4', 'Col-5', 'Col-6'],
		['v-1-1', 'v-1-2', 'v-1-3', 'v-1-4', 'v-1-5', 'v-1-6'],
		['v-2-1', 'v-2-2', 'v-2-3', 'v-2-4', 'v-2-5', 'v-2-6'],
		['v-3-1', 'v-3-2', 'v-3-3', 'v-3-4', 'v-3-5', 'v-3-6'],
		['v-4-1', 'v-4-2', 'v-4-3', 'v-4-4', 'v-4-5', 'v-4-6'],
		['v-5-1', 'v-5-2', 'v-5-3', 'v-5-4', 'v-5-5', 'v-5-6']
	]


d = [
		['Col-1', 'Col-2', 'Col-3', 'Col-4', 'Col-5', 'Col-7'],
		['v-1-1', 'v-1-2', 'v-1-3', 'v-1-4', 'v-1-5', 'v-1-7'],
		['v-2-1', 'v-2-2', 'v-9-3', 'v-8-4', 'v-2-5', 'v-2-7'],
		['v-3-1', 'v-3-2', 'v-3-3', 'v-3-4', 'v-7-5', 'v-3-7'],
		['v-5-1', 'v-5-2', 'v-5-3', 'v-5-4', 'v-5-5', 'v-5-7'],
		['v-6-1', 'v-6-2', 'v-6-3', 'v-6-4', 'v-6-5', 'v-6-7'],
	]


if __name__ == "__main__":
	print get_diff_matrix(d, c)














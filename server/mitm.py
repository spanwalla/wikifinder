from typing import Collection
from sqlalchemy.orm import Session
from . import crud


def get_paths(page_ids: Collection[int], visited: dict[int, list[int]]) -> list[list[int]]:
    paths = list()

    for page_id in page_ids:
        if page_id < 0:
            # Если пришли в вершину, из которой начинали обход, возвращаем пустой путь.
            return [[]]
        else:
            # Иначе рекурсивно идём к началу обхода, добавляя к полученным путям текущую страницу
            current_paths = get_paths(visited[page_id], visited)
            for path in current_paths:
                path.append(page_id)
                paths.append(path)

    return paths


def find_shortest_route(db: Session, source_page_id: int, target_page_id: int) -> set[tuple[int]]:
    if source_page_id == target_page_id:
        return {(source_page_id,)}

    # Словари содержат пары идентификатор статьи - список родительских статей (статей, из которых можно перейти в неё).
    # Для начальных вершин будем хранить -1, очевидно, дальше них нам идти не надо.
    unvisited_forward = {source_page_id: [-1]}
    unvisited_backward = {target_page_id: [-1]}

    visited_forward = dict()
    visited_backward = dict()

    paths = set()
    move_forward = True

    while len(paths) == 0 and unvisited_forward and unvisited_backward:
        if move_forward:
            outgoing_links = crud.read_outgoing_links(db, unvisited_forward.keys())
            process_links(outgoing_links, unvisited_forward, visited_forward)

        else:
            incoming_links = crud.read_incoming_links(db, unvisited_backward.keys())
            process_links(incoming_links, unvisited_backward, visited_backward)

        move_forward = not move_forward

        # Проверим, найден ли путь.
        # Если какая-то вершина содержится в результатах двух обходов одновременно, то путь найден.
        for page_id in unvisited_forward:
            if page_id in unvisited_backward:
                source_paths = get_paths(unvisited_forward[page_id], visited_forward)
                target_paths = get_paths(unvisited_backward[page_id], visited_backward)

                for target_path in target_paths:
                    target_path.reverse()
                    for source_path in source_paths:
                        paths.add(tuple(source_path + [page_id] + target_path))

    return paths


def process_links(links: dict[int, list[int]], unvisited: dict[int, list[int]], visited: dict[int, list[int]]):
    for page_id in unvisited:
        visited[page_id] = unvisited[page_id]

    unvisited.clear()

    for page_id, linked_page_ids in links.items():
        for linked_page_id in linked_page_ids:
            # Если ещё не были в связанной вершине, добавим её в список для обхода на следующей итерации,
            # а также отметим, что в неё можно попасть из текущей вершины.
            if (linked_page_id not in visited) and (linked_page_id not in unvisited):
                unvisited[linked_page_id] = [page_id]

            # Если вершина уже добавлена в список обхода, добавим информацию о наличии дополнительного пути к ней.
            elif linked_page_id in unvisited:
                unvisited[linked_page_id].append(page_id)
